# -*- coding: utf-8 -*-
"""
MCP Gateway Wrapper server.

Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Keval Mahajan, Mihai Criveti, Madhav Kandukuri

This module implements a wrapper bridge that facilitates
interaction between the MCP client and the MCP gateway.
It provides several functionalities, including listing tools,
invoking tools, managing resources, retrieving prompts,
and handling tool calls via the MCP gateway.

A **stdio** bridge that exposes a remote MCP Gateway
(HTTP-/JSON-RPC APIs) as a local MCP server. All JSON-RPC
traffic is written to **stdout**; every log or trace message
is emitted on **stderr** so that protocol messages and
diagnostics never mix.

Environment variables:
- MCP_SERVER_CATALOG_URLS: Comma-separated list of gateway catalog URLs (required)
- MCP_AUTH_TOKEN: Bearer token for the gateway (optional)
- MCP_TOOL_CALL_TIMEOUT: Seconds to wait for a gateway RPC call (default 90)
- MCP_WRAPPER_LOG_LEVEL: Python log level name or OFF/NONE to disable logging (default INFO)

Example:
    $ export MCPGATEWAY_BEARER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token --username admin --exp 10080 --secret my-test-key)
    $ export MCP_AUTH_TOKEN=${MCPGATEWAY_BEARER_TOKEN}
    $ export MCP_SERVER_CATALOG_URLS='http://localhost:4444/servers/UUID_OF_SERVER_1'
    $ export MCP_TOOL_CALL_TIMEOUT=120
    $ export MCP_WRAPPER_LOG_LEVEL=DEBUG # OFF to disable logging
    $ python3 -m mcpgateway.wrapper
"""

# Standard
import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

# Third-Party
import httpx
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from pydantic import AnyUrl

# First-Party
from mcpgateway import __version__
from mcpgateway.utils.retry_manager import ResilientHttpClient

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
ENV_SERVER_CATALOGS = "MCP_SERVER_CATALOG_URLS"
ENV_AUTH_TOKEN = "MCP_AUTH_TOKEN"  # nosec B105 - this is an *environment variable name*, not a secret
ENV_TIMEOUT = "MCP_TOOL_CALL_TIMEOUT"
ENV_LOG_LEVEL = "MCP_WRAPPER_LOG_LEVEL"

RAW_CATALOGS: str = os.getenv(ENV_SERVER_CATALOGS, "")
SERVER_CATALOG_URLS: List[str] = [u.strip() for u in RAW_CATALOGS.split(",") if u.strip()]

AUTH_TOKEN: str = os.getenv(ENV_AUTH_TOKEN, "")
TOOL_CALL_TIMEOUT: int = int(os.getenv(ENV_TIMEOUT, "90"))

# Validate required configuration (only when run as script)
if __name__ == "__main__" and not SERVER_CATALOG_URLS:
    print(f"Error: {ENV_SERVER_CATALOGS} environment variable is required", file=sys.stderr)
    sys.exit(1)


# -----------------------------------------------------------------------------
# Base URL Extraction
# -----------------------------------------------------------------------------
def _extract_base_url(url: str) -> str:
    """Return the gateway-level base URL.

    The function keeps any application root path (`APP_ROOT_PATH`) that the
    remote gateway is mounted under (for example `/gateway`) while removing
    the `/servers/<id>` suffix that appears in catalog endpoints. It also
    discards any query string or fragment.

    Args:
        url (str): Full catalog URL, e.g.
            `https://host.com/gateway/servers/UUID_OF_SERVER_1`.

    Returns:
        str: Clean base URL suitable for building `/tools/`, `/prompts/`,
        or `/resources/` endpoints-for example
        `https://host.com/gateway`.

    Raises:
        ValueError: If *url* lacks a scheme or network location.

    Examples:
        >>> _extract_base_url("https://host.com/servers/UUID_OF_SERVER_2")
        'https://host.com'
        >>> _extract_base_url("https://host.com/gateway/servers/UUID_OF_SERVER_2")
        'https://host.com/gateway'
        >>> _extract_base_url("https://host.com/gateway/servers")
        'https://host.com/gateway'
        >>> _extract_base_url("https://host.com/gateway")
        'https://host.com/gateway'
        >>> _extract_base_url("invalid-url")
        Traceback (most recent call last):
            ...
        ValueError: Invalid URL provided: invalid-url
        >>> _extract_base_url("https://host.com/")
        'https://host.com/'
        >>> _extract_base_url("https://host.com")
        'https://host.com'

    Note:
        If the target server was started with `APP_ROOT_PATH=/gateway`, the
        resulting catalog URLs include that prefix.  This helper preserves the
        prefix so the wrapper's follow-up calls remain correctly scoped.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL provided: {url}")

    path = parsed.path or ""
    if "/servers/" in path:
        path = path.split("/servers")[0]  # ".../servers/UUID_OF_SERVER_123" -> "..."
    elif path.endswith("/servers"):
        path = path[: -len("/servers")]  # ".../servers"     -> "..."
    # otherwise keep the existing path (supports APP_ROOT_PATH)

    return f"{parsed.scheme}://{parsed.netloc}{path}"


BASE_URL: str = _extract_base_url(SERVER_CATALOG_URLS[0]) if SERVER_CATALOG_URLS else ""

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
_log_level = os.getenv(ENV_LOG_LEVEL, "INFO").upper()
if _log_level in {"OFF", "NONE", "DISABLE", "FALSE", "0"}:
    logging.disable(logging.CRITICAL)
else:
    logging.basicConfig(
        level=getattr(logging, _log_level, logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        stream=sys.stderr,
    )

logger = logging.getLogger("mcpgateway.wrapper")
logger.info(f"Starting MCP wrapper {__version__}: base_url={BASE_URL}, timeout={TOOL_CALL_TIMEOUT}")


# -----------------------------------------------------------------------------
# HTTP Helpers
# -----------------------------------------------------------------------------
async def fetch_url(url: str) -> httpx.Response:
    """
    Perform an asynchronous HTTP GET request and return the response.

    This function makes authenticated HTTP requests to the MCP gateway using
    optional bearer token authentication and timeout configuration.

    Args:
        url: The target URL to fetch.

    Returns:
        The successful ``httpx.Response`` object.

    Raises:
        httpx.RequestError:    If a network problem occurs while making the request.
        httpx.HTTPStatusError: If the server returns a 4xx or 5xx response.

    Examples:
        Basic usage (requires running server):

        >>> import asyncio
        >>> # This example would require a real server running
        >>> # async def example():
        >>> #     response = await fetch_url("https://httpbin.org/get")
        >>> #     return response.status_code
        >>> # asyncio.run(example())  # Would return 200

        Error handling:

        >>> import asyncio
        >>> async def test_invalid_url():
        ...     try:
        ...         await fetch_url("http://invalid-domain-that-does-not-exist.test")
        ...     except Exception as e:
        ...         return type(e).__name__
        >>> # asyncio.run(test_invalid_url())  # Would return 'ConnectError' or similar
    """
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"} if AUTH_TOKEN else {}
    async with ResilientHttpClient(client_args={"timeout": TOOL_CALL_TIMEOUT}) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response
        except httpx.RequestError as err:
            logger.error(f"Network error while fetching {url}: {err}")
            raise
        except httpx.HTTPStatusError as err:
            logger.error(f"HTTP {err.response.status_code} returned for {url}: {err}")
            raise


# -----------------------------------------------------------------------------
# Metadata Helpers
# -----------------------------------------------------------------------------
async def get_tools_from_mcp_server(catalog_urls: List[str]) -> List[str]:
    """
    Retrieve associated tool IDs from the MCP gateway server catalogs.

    This function extracts server IDs from catalog URLs, fetches the server
    catalog from the gateway, and returns all tool IDs associated with the
    specified servers.

    Args:
        catalog_urls (List[str]): List of catalog endpoint URLs.

    Returns:
        List[str]: A list of tool ID strings extracted from the server catalog.

    Examples:
        Basic usage:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     urls = ["https://gateway.example.com/servers/server-123"]
        ...     # Would return tool IDs like ["tool1", "tool2"]
        ...     return ["get_time", "calculate_sum"]
        >>> asyncio.run(example())
        ['get_time', 'calculate_sum']

        Empty catalog handling:

        >>> import asyncio
        >>> async def empty_example():
        ...     return []  # No tools found
        >>> asyncio.run(empty_example())
        []
    """
    server_ids = [url.split("/")[-1] for url in catalog_urls]
    url = f"{BASE_URL}/servers/"
    response = await fetch_url(url)
    catalog = response.json()
    tool_ids: List[str] = []
    for entry in catalog:
        if str(entry.get("id")) in server_ids:
            tool_ids.extend(entry.get("associatedTools", []))
    return tool_ids


async def tools_metadata(tool_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch metadata for a list of MCP tools by their IDs.

    Retrieves detailed metadata including name, description, and input schema
    for each specified tool from the gateway's tools endpoint.

    Args:
        tool_ids (List[str]): List of tool ID strings.

    Returns:
        List[Dict[str, Any]]: A list of metadata dictionaries for each tool.

    Examples:
        Fetching specific tools:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     tool_ids = ["get_time", "calculate_sum"]
        ...     # Would return metadata like:
        ...     return [
        ...         {"name": "get_time", "description": "Get current time", "inputSchema": {}},
        ...         {"name": "calculate_sum", "description": "Add numbers", "inputSchema": {}}
        ...     ]
        >>> result = asyncio.run(example())
        >>> len(result)
        2

        Empty list handling:

        >>> import asyncio
        >>> async def empty_tools():
        ...     return []  # No tools to fetch
        >>> asyncio.run(empty_tools())
        []

        Special "0" ID for all tools:

        >>> # tool_ids = ["0"] returns all available tools
        >>> # This is handled by the conditional logic in the function
    """
    if not tool_ids:
        return []
    url = f"{BASE_URL}/tools/"
    response = await fetch_url(url)
    data: List[Dict[str, Any]] = response.json()
    if tool_ids == ["0"]:
        return data

    return [tool for tool in data if tool["name"] in tool_ids]


async def get_prompts_from_mcp_server(catalog_urls: List[str]) -> List[str]:
    """
    Retrieve associated prompt IDs from the MCP gateway server catalogs.

    Extracts server IDs from the provided catalog URLs and fetches all
    prompt IDs associated with those servers from the gateway.

    Args:
        catalog_urls (List[str]): List of catalog endpoint URLs.

    Returns:
        List[str]: A list of prompt ID strings.

    Examples:
        Basic prompt retrieval:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     urls = ["https://gateway.example.com/servers/server-123"]
        ...     # Would return prompt IDs like:
        ...     return ["greeting_prompt", "error_handler"]
        >>> asyncio.run(example())
        ['greeting_prompt', 'error_handler']

        No prompts available:

        >>> import asyncio
        >>> async def no_prompts():
        ...     return []  # Server has no prompts
        >>> asyncio.run(no_prompts())
        []
    """
    server_ids = [url.split("/")[-1] for url in catalog_urls]
    url = f"{BASE_URL}/servers/"
    response = await fetch_url(url)
    catalog = response.json()
    prompt_ids: List[str] = []
    for entry in catalog:
        if str(entry.get("id")) in server_ids:
            prompt_ids.extend(entry.get("associatedPrompts", []))
    return prompt_ids


async def prompts_metadata(prompt_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch metadata for a list of MCP prompts by their IDs.

    Retrieves detailed metadata including name, description, and arguments
    for each specified prompt from the gateway's prompts endpoint.

    Args:
        prompt_ids (List[str]): List of prompt ID strings.

    Returns:
        List[Dict[str, Any]]: A list of metadata dictionaries for each prompt.

    Examples:
        Fetching specific prompts:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     prompt_ids = ["greeting", "farewell"]
        ...     # Would return metadata like:
        ...     return [
        ...         {"name": "greeting", "description": "Welcome message", "arguments": []},
        ...         {"name": "farewell", "description": "Goodbye message", "arguments": []}
        ...     ]
        >>> result = asyncio.run(example())
        >>> len(result)
        2

        Empty prompt list:

        >>> import asyncio
        >>> async def no_prompts():
        ...     return []
        >>> asyncio.run(no_prompts())
        []

        All prompts with special ID:

        >>> # prompt_ids = ["0"] returns all available prompts
        >>> # This triggers the special case in the function
    """
    if not prompt_ids:
        return []
    url = f"{BASE_URL}/prompts/"
    response = await fetch_url(url)
    data: List[Dict[str, Any]] = response.json()
    if prompt_ids == ["0"]:
        return data
    return [pr for pr in data if str(pr.get("id")) in prompt_ids]


async def get_resources_from_mcp_server(catalog_urls: List[str]) -> List[str]:
    """
    Retrieve associated resource IDs from the MCP gateway server catalogs.

    Extracts server IDs from catalog URLs and fetches all resource IDs
    that are associated with those servers from the gateway.

    Args:
        catalog_urls (List[str]): List of catalog endpoint URLs.

    Returns:
        List[str]: A list of resource ID strings.

    Examples:
        Basic resource retrieval:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     urls = ["https://gateway.example.com/servers/server-123"]
        ...     # Would return resource IDs like:
        ...     return ["config.json", "readme.md", "schema.sql"]
        >>> asyncio.run(example())
        ['config.json', 'readme.md', 'schema.sql']

        No resources found:

        >>> import asyncio
        >>> async def no_resources():
        ...     return []  # Server has no resources
        >>> asyncio.run(no_resources())
        []
    """
    server_ids = [url.split("/")[-1] for url in catalog_urls]
    url = f"{BASE_URL}/servers/"
    response = await fetch_url(url)
    catalog = response.json()
    resource_ids: List[str] = []
    for entry in catalog:
        if str(entry.get("id")) in server_ids:
            resource_ids.extend(entry.get("associatedResources", []))
    return resource_ids


async def resources_metadata(resource_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch metadata for a list of MCP resources by their IDs.

    Retrieves detailed metadata including URI, name, description, and MIME type
    for each specified resource from the gateway's resources endpoint.

    Args:
        resource_ids (List[str]): List of resource ID strings.

    Returns:
        List[Dict[str, Any]]: A list of metadata dictionaries for each resource.

    Examples:
        Fetching specific resources:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     resource_ids = ["config", "readme"]
        ...     # Would return metadata like:
        ...     return [
        ...         {"id": "config", "uri": "file://config.json", "name": "Config", "mimeType": "application/json"},
        ...         {"id": "readme", "uri": "file://readme.md", "name": "README", "mimeType": "text/markdown"}
        ...     ]
        >>> result = asyncio.run(example())
        >>> len(result)
        2

        Empty resource list:

        >>> import asyncio
        >>> async def no_resources():
        ...     return []
        >>> asyncio.run(no_resources())
        []

        All resources with special ID:

        >>> # resource_ids = ["0"] returns all available resources
        >>> # This is handled by the conditional in the function
    """
    if not resource_ids:
        return []
    url = f"{BASE_URL}/resources/"
    response = await fetch_url(url)
    data: List[Dict[str, Any]] = response.json()
    if resource_ids == ["0"]:
        return data
    return [res for res in data if str(res.get("id")) in resource_ids]


# -----------------------------------------------------------------------------
# Server Handlers
# -----------------------------------------------------------------------------
server: Server = Server("mcpgateway-wrapper")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List all available MCP tools exposed by the gateway.

    Queries the configured server catalogs to retrieve tool IDs and then
    fetches metadata for each tool to construct a list of Tool objects.

    Returns:
        List[types.Tool]: A list of Tool instances including name, description, and input schema.

    Raises:
        RuntimeError: If an error occurs during fetching or processing.

    Examples:
        Successful tool listing:

        >>> import asyncio
        >>> # Mock example - would require real server and MCP setup
        >>> async def example():
        ...     # Would return Tool objects like:
        ...     from mcp import types
        ...     return [
        ...         types.Tool(name="get_time", description="Get current time", inputSchema={}),
        ...         types.Tool(name="calculate", description="Perform calculation", inputSchema={})
        ...     ]
        >>> # result = asyncio.run(example())
        >>> # len(result) would be 2

        Error handling:

        >>> # If gateway is unreachable, RuntimeError is raised
        >>> # try: tools = await handle_list_tools()
        >>> # except RuntimeError as e: print(f"Error: {e}")
    """
    try:
        tool_ids = ["0"] if SERVER_CATALOG_URLS[0] == BASE_URL else await get_tools_from_mcp_server(SERVER_CATALOG_URLS)
        metadata = await tools_metadata(tool_ids)
        tools = []
        for tool in metadata:
            tool_name = tool.get("name")
            if tool_name:  # Only include tools with valid names
                tools.append(
                    types.Tool(
                        name=str(tool_name),
                        description=tool.get("description", ""),
                        inputSchema=tool.get("inputSchema", {}),
                        annotations=tool.get("annotations", {}),
                    )
                )
        return tools
    except Exception as exc:
        logger.exception("Error listing tools")
        raise RuntimeError(f"Error listing tools: {exc}")


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Invoke a named MCP tool via the gateway's RPC endpoint.

    Sends a JSON-RPC request to the gateway to execute the specified tool
    with the provided arguments and returns the result as content objects.

    Args:
        name (str): The name of the tool to invoke.
        arguments (Optional[Dict[str, Any]]): The arguments to pass to the tool method.

    Returns:
        List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
            A list of content objects returned by the tool.

    Raises:
        ValueError: If tool call fails.
        RuntimeError: If the HTTP request fails or returns an error.

    Examples:
        Successful tool call:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     # Calling a time tool
        ...     from mcp import types
        ...     result = [types.TextContent(type="text", text="2024-01-15 10:30:00 UTC")]
        ...     return result
        >>> # result = asyncio.run(example())
        >>> # result[0].text would contain the timestamp

        Tool call with arguments:

        >>> import asyncio
        >>> async def calc_example():
        ...     # Calling calculator tool with arguments
        ...     from mcp import types
        ...     result = [types.TextContent(type="text", text="42")]
        ...     return result
        >>> # result = await handle_call_tool("add", {"a": 20, "b": 22})

        Error handling:

        >>> # Tool returns error
        >>> # try: await handle_call_tool("invalid_tool")
        >>> # except ValueError as e: print(f"Tool error: {e}")
        >>> # except RuntimeError as e: print(f"Network error: {e}")
    """
    if arguments is None:
        arguments = {}

    logger.info(f"Calling tool {name} with args {arguments}")
    payload = {"jsonrpc": "2.0", "id": 2, "method": name, "params": arguments}
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"} if AUTH_TOKEN else {}

    try:
        async with ResilientHttpClient(client_args={"timeout": TOOL_CALL_TIMEOUT}) as client:
            resp = await client.post(f"{BASE_URL}/rpc/", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                raise ValueError(f"Tool call failed: {error_msg}")

            tool_result = result.get("result", result)
            return [types.TextContent(type="text", text=str(tool_result))]

    except httpx.TimeoutException as exc:
        logger.error(f"Timeout calling tool {name}: {exc}")
        raise RuntimeError(f"Tool call timeout: {exc}")
    except Exception as exc:
        logger.exception(f"Error calling tool {name}")
        raise RuntimeError(f"Error calling tool: {exc}")


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    List all available MCP resources exposed by the gateway.

    Fetches resource IDs from the configured catalogs and retrieves
    metadata to construct Resource instances.

    Returns:
        List[types.Resource]: A list of Resource objects including URI, name, description, and MIME type.

    Raises:
        RuntimeError: If an error occurs during fetching or processing.

    Examples:
        Successful resource listing:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     from mcp import types
        ...     from pydantic import AnyUrl
        ...     return [
        ...         types.Resource(
        ...             uri=AnyUrl("file://config.json"),
        ...             name="Configuration",
        ...             description="App config file",
        ...             mimeType="application/json"
        ...         )
        ...     ]
        >>> # result = asyncio.run(example())
        >>> # result[0].name would be "Configuration"

        Empty resource list:

        >>> import asyncio
        >>> async def no_resources():
        ...     return []  # No resources available
        >>> asyncio.run(no_resources())
        []

        Invalid URI handling:

        >>> # Resources with invalid URIs are skipped with warnings
        >>> # The function filters out resources missing required fields
    """
    try:
        ids = ["0"] if SERVER_CATALOG_URLS[0] == BASE_URL else await get_resources_from_mcp_server(SERVER_CATALOG_URLS)
        meta = await resources_metadata(ids)
        resources = []
        for r in meta:
            uri = r.get("uri")
            if not uri:
                logger.warning(f"Resource missing URI, skipping: {r}")
                continue
            try:
                resources.append(
                    types.Resource(
                        uri=AnyUrl(uri),
                        name=r.get("name", ""),
                        description=r.get("description", ""),
                        mimeType=r.get("mimeType", "text/plain"),
                    )
                )
            except Exception as e:
                logger.warning(f"Invalid resource URI {uri}: {e}")
                continue
        return resources
    except Exception as exc:
        logger.exception("Error listing resources")
        raise RuntimeError(f"Error listing resources: {exc}")


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read and return the content of a resource by its URI.

    Fetches the resource content from the specified URI using the gateway's
    HTTP interface and returns the response body as text.

    Args:
        uri (AnyUrl): The URI of the resource to read.

    Returns:
        str: The body text of the fetched resource.

    Raises:
        ValueError: If the resource cannot be fetched.

    Examples:
        Reading a text resource:

        >>> import asyncio
        >>> from pydantic import AnyUrl
        >>> # Mock example - would require real server
        >>> async def example():
        ...     # Would return file content
        ...     return "{\\"version\\": \\"1.0\\", \\"name\\": \\"myapp\\"}"
        >>> # content = await handle_read_resource(AnyUrl("file://config.json"))
        >>> asyncio.run(example())
        '{"version": "1.0", "name": "myapp"}'

        Error handling:

        >>> # Invalid or unreachable URI
        >>> # try: content = await handle_read_resource(AnyUrl("file://missing.txt"))
        >>> # except ValueError as e: print(f"Read error: {e}")
    """
    try:
        response = await fetch_url(str(uri))
        return response.text
    except Exception as exc:
        logger.exception(f"Error reading resource {uri}")
        raise ValueError(f"Failed to read resource at {uri}: {exc}")


@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """
    List all available MCP prompts exposed by the gateway.

    Retrieves prompt IDs from the catalogs and fetches metadata
    to create Prompt instances.

    Returns:
        List[types.Prompt]: A list of Prompt objects including name, description, and arguments.

    Raises:
        RuntimeError: If an error occurs during fetching or processing.

    Examples:
        Successful prompt listing:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     from mcp import types
        ...     return [
        ...         types.Prompt(
        ...             name="greeting",
        ...             description="Welcome message template",
        ...             arguments=[{"name": "username", "description": "User's name"}]
        ...         ),
        ...         types.Prompt(
        ...             name="error_msg",
        ...             description="Error message template",
        ...             arguments=[{"name": "error_code", "description": "Error code"}]
        ...         )
        ...     ]
        >>> result = asyncio.run(example())
        >>> len(result)
        2

        Empty prompt list:

        >>> import asyncio
        >>> async def no_prompts():
        ...     return []
        >>> asyncio.run(no_prompts())
        []
    """
    try:
        ids = ["0"] if SERVER_CATALOG_URLS[0] == BASE_URL else await get_prompts_from_mcp_server(SERVER_CATALOG_URLS)
        meta = await prompts_metadata(ids)
        prompts = []
        for p in meta:
            prompt_name = p.get("name")
            if prompt_name:  # Only include prompts with valid names
                prompts.append(
                    types.Prompt(
                        name=str(prompt_name),
                        description=p.get("description", ""),
                        arguments=p.get("arguments", []),
                    )
                )
        return prompts
    except Exception as exc:
        logger.exception("Error listing prompts")
        raise RuntimeError(f"Error listing prompts: {exc}")


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
    """
    Retrieve and format a single prompt template with provided arguments.

    Fetches the prompt template from the gateway and formats it using the
    provided arguments, returning a structured prompt result.

    Args:
        name (str): The unique name of the prompt to fetch.
        arguments (Optional[Dict[str, str]]): A mapping of placeholder names to replacement values.

    Returns:
        types.GetPromptResult: Contains description and list of formatted PromptMessage instances.

    Raises:
        ValueError: If fetching or formatting fails.

    Examples:
        Basic prompt retrieval:

        >>> import asyncio
        >>> # Mock example - would require real server
        >>> async def example():
        ...     from mcp import types
        ...     return types.GetPromptResult(
        ...         description="Welcome message",
        ...         messages=[
        ...             types.PromptMessage(
        ...                 role="user",
        ...                 content=types.TextContent(type="text", text="Hello Alice!")
        ...             )
        ...         ]
        ...     )
        >>> # result = await handle_get_prompt("greeting", {"username": "Alice"})

        Template formatting:

        >>> # Prompt template: "Hello {username}!"
        >>> # Arguments: {"username": "Bob"}
        >>> # Result: "Hello Bob!"

        Missing argument error:

        >>> # Template requires {username} but no arguments provided
        >>> # try: await handle_get_prompt("greeting")
        >>> # except ValueError as e: print(f"Missing placeholder: {e}")

        Prompt not found:

        >>> # try: await handle_get_prompt("nonexistent")
        >>> # except ValueError as e: print(f"Prompt error: {e}")
    """
    try:
        url = f"{BASE_URL}/prompts/{name}"
        response = await fetch_url(url)
        prompt_data = response.json()

        template = prompt_data.get("template", "")
        try:
            formatted = template.format(**(arguments or {}))
        except KeyError as exc:
            raise ValueError(f"Missing placeholder in arguments: {exc}")
        except Exception as exc:
            raise ValueError(f"Error formatting prompt: {exc}")

        return types.GetPromptResult(
            description=prompt_data.get("description", ""),
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=formatted),
                )
            ],
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(f"Error getting prompt {name}")
        raise ValueError(f"Failed to fetch prompt '{name}': {exc}")


async def main() -> None:
    """
    Main entry point to start the MCP stdio server.

    Initializes the server over standard IO, registers capabilities,
    and begins listening for JSON-RPC messages. This function handles
    the complete server lifecycle including graceful shutdown.

    This function should only be called in a script context.

    Raises:
        RuntimeError: If the server fails to start.

    Examples:
        Starting the server:

        >>> import asyncio
        >>> # In a real script context:
        >>> # if __name__ == "__main__":
        >>> #     asyncio.run(main())

        Server initialization:

        >>> # Server starts with stdio transport
        >>> # Registers MCP capabilities for tools, prompts, resources
        >>> # Begins processing JSON-RPC messages from stdin
        >>> # Sends responses to stdout

        Error handling:

        >>> # Server startup failures raise RuntimeError
        >>> # Keyboard interrupts are handled gracefully
        >>> # All errors are logged appropriately
    """
    try:
        async with mcp.server.stdio.stdio_server() as (reader, writer):
            await server.run(
                reader,
                writer,
                InitializationOptions(
                    server_name="mcpgateway-wrapper",
                    server_version=__version__,
                    capabilities=server.get_capabilities(notification_options=NotificationOptions(), experimental_capabilities={}),
                ),
            )
    except Exception as exc:
        logger.exception("Server failed to start")
        raise RuntimeError(f"Server startup failed: {exc}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception:
        logger.exception("Server failed")
        sys.exit(1)
    finally:
        logger.info("Wrapper shutdown complete")
