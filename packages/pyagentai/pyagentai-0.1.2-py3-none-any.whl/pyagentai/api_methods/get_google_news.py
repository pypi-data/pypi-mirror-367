from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_google_news(
    self: AgentAIClient,
    query: str,
    date_range: str = "24h",
    location: str | None = None,
) -> dict[str, Any]:
    """Fetch news articles based on queries and date ranges to stay updated on
    relevant topics or trends.

    For more details, see the `official Get Google News API documentation
    <https://docs.agent.ai/api-reference/get-data/google-news-data>`_.

    Args:
        query: The keywords to search for.
        date_range: The time frame for the news search. Can be one of:
            - ``24h``: Last 24 hours
            - ``7d``: Last 7 days
            - ``30d``: Last 30 days
            - ``90d``: Last 90 days
        location: The location to filter news results. Defaults to None.

    Returns:
        A dictionary containing the news articles related to the query.

    Raises:
        ValueError: If the provided query is invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not date_range or not date_range.strip():
        raise ValueError("Date range cannot be empty.")

    if location and not location.strip():
        raise ValueError("Location cannot be empty.")

    endpoint = self.config.endpoints.get_google_news
    data: dict[str, Any] = {}

    data["query"] = query.strip()
    data["date_range"] = date_range.strip()

    if location:
        data["location"] = location.strip()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    news_data: dict[str, Any] = response_data.get("response", {})

    return news_data
