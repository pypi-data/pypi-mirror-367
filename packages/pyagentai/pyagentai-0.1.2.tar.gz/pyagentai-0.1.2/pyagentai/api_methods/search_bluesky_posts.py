from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def search_bluesky_posts(
    self: AgentAIClient,
    query: str,
    num_posts: int = 1,
) -> dict[str, Any]:
    """Search for Bluesky posts matching specific keywords or criteria to
    gather social media insights.

    For more details, see the `official Search Bluesky Posts API documentation
    <https://docs.agent.ai/api-reference/get-data/search-bluesky-posts>`_.

    Args:
        query: The keywords to search for.
        num_posts: The number of results to retrieve. Can be one of:
            - ``1``: 1 result
            - ``5``: 5 results
            - ``10``: 10 results
            - ``25``: 25 results
            - ``50``: 50 results
            - ``100``: 100 results

            Defaults to ``1``.

    Returns:
        A dictionary containing the search results from the specified Bluesky
        posts including metrics like reposts, likes, and replies.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not isinstance(num_posts, int) or num_posts <= 0:
        raise ValueError("Number of posts must be a positive integer.")

    endpoint = self.config.endpoints.search_bluesky_posts
    data: dict[str, Any] = {}

    data["query"] = query.strip()
    data["num_posts"] = num_posts

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    bluesky_data: dict[str, Any] = response_data.get("response", {})

    return bluesky_data
