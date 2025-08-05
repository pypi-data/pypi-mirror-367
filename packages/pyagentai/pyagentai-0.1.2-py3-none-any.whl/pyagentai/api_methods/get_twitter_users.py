from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_twitter_users(
    self: AgentAIClient,
    keywords: str,
    num_users: int = 1,
) -> list[str]:
    """Search and retrieve Twitter user profiles based on specific keywords
    for targeted social media analysis.

    For more details, see the `official Get Twitter Users API documentation
    <https://docs.agent.ai/api-reference/get-data/get-twitter-users>`_.

    Args:
        keywords: The keywords to search for.
        num_users: The number of user profiles to retrieve. Can be one of:
            - ``1``: 1 user
            - ``5``: 5 users
            - ``10``: 10 users
            - ``25``: 25 users
            - ``50``: 50 users
            - ``100``: 100 users

            Defaults to ``1``.

    Returns:
        A list of Twitter user profiles.

    Raises:
        ValueError: If the provided keywords are invalid or num_users is
            not one of the allowed values.
    """
    if not keywords or not keywords.strip():
        raise ValueError("Keywords cannot be empty.")

    endpoint = self.config.endpoints.get_twitter_users
    data: dict[str, Any] = {}

    data["keywords"] = keywords.strip()
    data["num_users"] = num_users

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()

    # The API returns a list of Twitter user profiles
    response_users: list[str] = response_data.get("response", [])

    return response_users
