from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def find_linkedin_profile(
    self: AgentAIClient,
    query: str,
) -> str:
    """Find the LinkedIn profile slug for a person.

    For more details, see the `official Find LinkedIn Profile API documentation
    <https://docs.agent.ai/api-reference/get-data/find-linkedin-profile>`_.

    Args:
        query: The text query to find the LinkedIn profile slug.

    Returns:
        A string containing the LinkedIn profile slug.

    Raises:
        ValueError: If the provided query is invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    endpoint = self.config.endpoints.find_linkedin_profile
    data: dict[str, Any] = {}

    data["query"] = query.strip()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    response_slug: str = response_data.get("response", "")

    return response_slug
