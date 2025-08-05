from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_instagram_followers(
    self: AgentAIClient,
    username: str,
    limit: int = 20,
) -> dict[str, Any]:
    """Retrieve a list of top followers from a specified Instagram account for
    social media analysis.

    For more details, see the `official Get Instagram Followers API
    documentation
    <https://docs.agent.ai/api-reference/get-data/get-instagram-followers>`_.

    Args:
        username: The Instagram username to fetch profile from.
        limit: The number of top followers to retrieve.
            Can be one of:
            - ``10``: 10 followers
            - ``20``: 20 followers
            - ``50``: 50 followers
            - ``100``: 100 followers

            Defaults to ``20``.

    Returns:
        A dictionary containing the list of top followers from the specified
        Instagram account including their profile information, follower count,
        and other relevant metrics.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    if not username or not username.strip():
        raise ValueError("Username cannot be empty.")

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    endpoint = self.config.endpoints.get_instagram_followers
    data: dict[str, Any] = {}

    data["username"] = username.strip()
    data["limit"] = str(limit)

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    instagram_data: dict[str, Any] = response_data.get("response", {})

    return instagram_data
