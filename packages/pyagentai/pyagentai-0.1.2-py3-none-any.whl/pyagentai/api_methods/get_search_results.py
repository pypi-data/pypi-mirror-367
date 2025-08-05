from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_search_results(
    self: AgentAIClient,
    query: str,
    search_engine: str = "google",
    num_posts: int = 10,
) -> dict[str, Any]:
    """Fetch search results from Google or YouTube for specific queries,
    providing valuable insights and content.

    For more details, see the `official Get Search Results API documentation
    <https://docs.agent.ai/api-reference/get-data/search-results>`_.

    Args:
        query: The keywords to search for.
        search_engine: The search engine to use. Can be one of:
            - ``"google"``: Google
            - ``"youtube"``: YouTube
            - ``"youtube_channel"``: YouTube Channel
        num_posts: The number of results to retrieve. Can be one of:
            - ``1``: 1 result
            - ``5``: 5 results
            - ``10``: 10 results
            - ``25``: 25 results
            - ``50``: 50 results
            - ``100``: 100 results

    Returns:
        A dictionary containing the search results from the specified search
        engine.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not search_engine or not search_engine.strip():
        raise ValueError("Search engine cannot be empty.")

    if not isinstance(num_posts, int) or num_posts <= 0:
        raise ValueError("Number of posts must be a positive integer.")

    endpoint = self.config.endpoints.get_search_results
    data: dict[str, Any] = {}

    data["query"] = query.strip()
    data["search_engine"] = search_engine.strip().lower()
    data["num_posts"] = num_posts

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    search_data: dict[str, Any] = response_data.get("response", {})

    return search_data
