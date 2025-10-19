"""Async client helpers for the toy finance MCP server."""

import asyncio
from dataclasses import asdict, is_dataclass
from typing import Any
import mcp.types
from fastmcp.client.client import CallToolResult, Client
from fastmcp.client.transports import StreamableHttpTransport
from .server import DEFAULT_HOST, DEFAULT_PATH, DEFAULT_PORT


DEFAULT_ENDPOINT = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}{DEFAULT_PATH}"


def _create_client(endpoint: str) -> Client[StreamableHttpTransport]:
    """Return a client configured for the toy finance server."""
    transport = StreamableHttpTransport(url=endpoint)
    return Client(transport)


async def list_tools(endpoint: str = DEFAULT_ENDPOINT) -> list[mcp.types.Tool]:
    """Return the list of tools published by the toy finance server."""
    client = _create_client(endpoint)
    async with client:
        return await client.list_tools()


def _result_to_dict(result: CallToolResult) -> dict[str, Any]:
    """Normalize a CallToolResult into a plain dictionary."""
    if result.data is not None:
        data = result.data
        if hasattr(data, "model_dump"):
            return data.model_dump()
        if is_dataclass(data):
            return asdict(data)
        if isinstance(data, dict):
            return data

    if isinstance(result.structured_content, dict):
        return result.structured_content

    # Fallback to text content
    for block in result.content or []:
        if isinstance(block, mcp.types.TextContent):
            return {"raw": block.text}

    return {}


async def get_stock_price(symbol: str, endpoint: str = DEFAULT_ENDPOINT) -> dict[str, Any]:
    """Call the MCP tool and return the stock payload."""
    client = _create_client(endpoint)
    async with client:
        result = await client.call_tool("get_stock_price", {"symbol": symbol})
    data = _result_to_dict(result)
    if "symbol" not in data:
        data["symbol"] = symbol.upper()
    return data


async def _demo(symbol: str) -> None:
    print("\n=== Tools Available ===")
    tools = await list_tools()
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    print(f"\n=== Calling get_stock_price({symbol!r}) ===")
    result = await get_stock_price(symbol)
    print("Response:", result)


if __name__ == "__main__":
    asyncio.run(_demo("AAPL"))
