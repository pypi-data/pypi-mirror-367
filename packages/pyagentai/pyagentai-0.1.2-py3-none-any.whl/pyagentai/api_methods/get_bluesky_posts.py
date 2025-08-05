from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_bluesky_posts(
    self: AgentAIClient,
    handle: str,
    num_posts: int = 5,
) -> dict[str, Any]:
    """Fetch recent posts from a specified Bluesky user handle, making it easy
    to monitor activity on the platform.

    For more details, see the `official Get Bluesky Posts API documentation
    <https://docs.agent.ai/api-reference/get-data/get-bluesky-posts>`_.

    Args:
        handle: The Bluesky handle to fetch recent posts from.
        num_posts: The number of posts to return.
            Can be one of:
            - ``1``: 1 post
            - ``5``: 5 posts
            - ``10``: 10 posts
            - ``25``: 25 posts
            - ``50``: 50 posts
            - ``100``: 100 posts

            Defaults to ``5``.

    Returns:
        A dictionary containing the recent posts from the specified Bluesky
        handle, including metrics like reposts, likes, and replies.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    if not handle or not handle.strip():
        raise ValueError("Bluesky handle cannot be empty.")

    if not isinstance(num_posts, int) or num_posts <= 0:
        raise ValueError("Number of posts must be a positive integer.")

    endpoint = self.config.endpoints.get_bluesky_posts
    data: dict[str, Any] = {}

    data["handle"] = handle.strip()
    data["num_posts"] = num_posts

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    bluesky_data: dict[str, Any] = response_data.get("response", {})

    return bluesky_data
