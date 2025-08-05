import os
from typing import Any

import pytest
from fastmcp import Client

from .mcp_server import mcp


@pytest.fixture(scope="session")
def mcp_client() -> Client[Any]:
    """Create a FastMCP client for testing."""
    return Client(mcp)


@pytest.mark.asyncio
async def test_read_resource_torrent_categories(mcp_client: Client[Any]) -> None:
    """Test reading the 'torrent_categories' resource."""
    async with mcp_client as client:
        result = await client.read_resource("data://torrent_categories")
        assert result is not None and len(result[0].text) > 8  # At least 1 category


@pytest.mark.asyncio
async def test_search_torrents(mcp_client: Client[Any]) -> None:
    """Test the 'search_torrents' tool."""
    async with mcp_client as client:
        result = await client.call_tool(
            "search_torrents",
            {"query": "berserk", "categories": ["anime serie"], "max_items": 3},
        )
        assert (
            result is not None and len(result.content[0].text) > 32
        )  # At least 1 torrent found


@pytest.mark.asyncio
async def test_get_torrent_details(mcp_client: Client[Any]) -> None:
    """Test the 'get_torrent_details' tool."""
    async with mcp_client as client:
        result = await client.call_tool("get_torrent_details", {"torrent_id": 1268760})
        assert result is not None and len(result.content[0].text) > 32  # Torrent found


@pytest.mark.asyncio
async def test_get_magnet_link(mcp_client: Client[Any]) -> None:
    """Test the 'get_magnet_link' tool."""
    async with mcp_client as client:
        result = await client.call_tool("get_magnet_link", {"torrent_id": 1268760})
        assert (
            result is not None and len(result.content[0].text) > 32
        )  # Magnet link found


@pytest.mark.asyncio
async def test_download_torrent_file(mcp_client: Client[Any]) -> None:
    """Test the 'download_torrent_file' tool."""
    async with mcp_client as client:
        curr_dir = os.getcwd()
        result = await client.call_tool(
            "download_torrent_file", {"torrent_id": 1268760, "output_dir": curr_dir}
        )
        assert (
            result is not None and len(result.content[0].text) > 4
        )  # Torrent file found
        if result:
            file_path = os.path.join(curr_dir, result.content[0].text)
            if os.path.exists(file_path):
                os.remove(file_path)
