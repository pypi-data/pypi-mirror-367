from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def run_youtube_search(
    self: AgentAIClient,
    query: str,
) -> dict[str, Any]:
    """Perform a YouTube search and retrieve results for specified queries.

    For more details, see the `official Run YouTube Search API documentation
    <https://docs.agent.ai/api-reference/get-data/youtube-search-results>`_.

    Args:
        query: The keywords to search for.

    Returns:
        A dictionary containing the YouTube search results - videos, shorts,
        suggestions and channels.

    Raises:
        ValueError: If the provided query is invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    endpoint = self.config.endpoints.run_youtube_search
    data: dict[str, Any] = {}

    data["query"] = query.strip()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    youtube_data: dict[str, Any] = response_data.get("response", {})

    return youtube_data
