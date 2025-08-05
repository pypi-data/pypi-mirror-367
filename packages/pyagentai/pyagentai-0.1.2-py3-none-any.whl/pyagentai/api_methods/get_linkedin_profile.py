from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_linkedin_profile(
    self: AgentAIClient,
    profile_handle: str,
) -> dict[str, Any]:
    """Retrieve detailed information from a specified LinkedIn profile.

    For more details, see the `official Get LinkedIn Profile API documentation
    <https://docs.agent.ai/api-reference/get-data/get-linkedin-profile>`_.

    Args:
        profile_handle: The LinkedIn handle to fetch profile from.

    Returns:
        A dictionary containing the profile information from the specified
        LinkedIn handle.

    Raises:
        ValueError: If the provided profile handle is invalid.
    """
    if not profile_handle or not profile_handle.strip():
        raise ValueError("Profile handle cannot be empty.")

    endpoint = self.config.endpoints.get_linkedin_profile
    data: dict[str, Any] = {}

    data["profile_handle"] = profile_handle.strip()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    profile_data: dict[str, Any] = response_data.get("response", {})

    return profile_data
