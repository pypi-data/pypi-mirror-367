from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_instagram_profile(
    self: AgentAIClient,
    username: str,
) -> dict[str, Any]:
    """Fetch detailed profile information for a specified Instagram username.

    For more details, see the `official Get Instagram Profile API documentation
    <https://docs.agent.ai/api-reference/get-data/get-instagram-profile>`_.

    Args:
        username: The Instagram username to fetch profile from.

    Returns:
        A dictionary containing the profile information from the specified
        Instagram username.

    Raises:
        ValueError: If the provided username is invalid.
    """
    if not username or not username.strip():
        raise ValueError("Username cannot be empty.")

    endpoint = self.config.endpoints.get_instagram_profile
    data: dict[str, Any] = {}

    data["username"] = username.strip()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    instagram_data: dict[str, Any] = response_data.get("response", {})

    return instagram_data
