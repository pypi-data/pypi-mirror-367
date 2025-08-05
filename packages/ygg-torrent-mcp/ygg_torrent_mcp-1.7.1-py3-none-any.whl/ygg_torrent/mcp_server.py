import logging
from typing import Any

from fastmcp import FastMCP

from .wrapper import Torrent, YggTorrentApi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("YggTorrent")

mcp: FastMCP[Any] = FastMCP("YggTorrent Tool")
ygg_api = YggTorrentApi()


@mcp.resource("data://torrent_categories")
def torrent_categories() -> list[str]:
    """Get a list of available torrent categories."""
    return ygg_api.get_torrent_categories()


@mcp.tool()
def prepare_search_query(user_intent: str, search_query: str) -> str:
    """Always use this tool to prepare a query for `search_torrents`.
    Properly split the user's intention and the actual search query (space-separated keywords) to avoid unfruitful results.
    # Instructions:
    - `user_intent`: Must reflect user's overall intention (e.g., "last episode of Breaking Bad", "season 5 of Breaking Bad", "complete series of Breaking Bad").
    - `search_query`: The actual search terms, consisting of lowercase, space-separated keywords. Do not add generic terms (e.g., "movie", "series"), common prefixes (e.g., "the", "a", "and"), or extra information (e.g., episode name, resolution, codec). For TV series, use `sXXeYY` for specific episodes (e.g., "breaking bad s05e16"), `sXX` for complete seasons (e.g., "breaking bad s05") and only the show name for complete series (e.g., "breaking bad").
    - For non-French language, if requested, just add 'multi' to the query
    """
    return "Ready to search for torrents."


@mcp.tool()
def search_torrents(
    query: str,
    categories: list[str] | None = None,
    page: int = 1,
    per_page: int = 25,
    order_by: str = "seeders",
    max_items: int = 25,
) -> str:
    """Searches for torrents on YggTorrent using a query (space-separated keywords) and returns a list of torrent results.
    # Instructions:
    - To be called after `prepare_search_query`.
    - Provide **only** `query`, except if user mentions other parameters.
    - Prioritize results using the following hierarchy: is 1080p > smaller file size > is x265 > max seeders+leechers.
    - Recommend up to 3 of the best results, **always** providing filename, file size, seeders/leechers, date, source, and an ultra concise reason.
    - If the search results are too broad, suggest the user provide more specific keywords.
    - Keep recommendations and suggestions concise."""
    logger.info(
        f"Searching for torrents: {query}, categories: {categories}, page: {page}, per_page: {per_page}, order_by: {order_by}, max_items: {max_items}"
    )
    torrents: list[Torrent] = ygg_api.search_torrents(
        query, categories, page, per_page, order_by
    )[:max_items]
    return "\n".join([str(torrent) for torrent in torrents])


@mcp.tool()
def get_torrent_details(torrent_id: int) -> str | None:
    """Get details from YggTorrent about a specific torrent by id."""
    logger.info(f"Getting details for torrent: {torrent_id}")
    torrent: Torrent | None = ygg_api.get_torrent_details(
        torrent_id, with_magnet_link=True
    )
    return str(torrent) if torrent else "Torrent not found"


@mcp.tool()
def get_magnet_link(torrent_id: int) -> str | None:
    """Get the magnet link from YggTorrent for a specific torrent by id."""
    logger.info(f"Getting magnet link for torrent: {torrent_id}")
    magnet_link: str | None = ygg_api.get_magnet_link(torrent_id)
    return magnet_link or "Magnet link not found"


@mcp.tool()
def download_torrent_file(
    torrent_id: int,
    output_dir: str,
) -> str | None:
    """Download the torrent file from YggTorrent for a specific torrent by id."""
    logger.info(f"Downloading torrent file for torrent: {torrent_id}")
    return ygg_api.download_torrent_file(torrent_id, output_dir)
