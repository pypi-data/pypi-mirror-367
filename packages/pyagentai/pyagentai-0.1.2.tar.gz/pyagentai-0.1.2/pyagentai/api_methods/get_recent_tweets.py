from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_recent_tweets(
    self: AgentAIClient,
    profile_handle: str,
    recent_tweets_count: int = 1,
) -> dict[str, Any]:
    """Fetch recent tweets from a specified Twitter handle.

    For more details, see the `official Get Recent Tweets API documentation
    <https://docs.agent.ai/api-reference/get-data/get-recent-tweets>`_.

    Args:
        profile_handle: The Twitter handle to fetch recent tweets from.
        recent_tweets_count: The number of tweets to return.

    Returns:
        A dictionary containing the recent tweets from the specified Twitter
        handle, including metrics like retweets, likes, and replies.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    if not profile_handle or not profile_handle.strip():
        raise ValueError("Profile handle cannot be empty.")

    if not isinstance(recent_tweets_count, int) or recent_tweets_count <= 0:
        raise ValueError("Number of tweets must be a positive integer.")

    endpoint = self.config.endpoints.get_recent_tweets
    data: dict[str, Any] = {}

    data["profile_handle"] = profile_handle.strip()
    data["recent_tweets_count"] = str(recent_tweets_count)

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    tweets_data: dict[str, Any] = response_data.get("response", {})

    return tweets_data
