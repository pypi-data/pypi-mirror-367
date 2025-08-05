from typing import Any
from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_linkedin_activity(
    self: AgentAIClient,
    profile_urls: list[str],
    num_posts: int = 3,
) -> dict[str, Any]:
    """Retrieve recent LinkedIn posts from specified profiles to analyze
    professional activity and engagement.

    For more details, see the `official Get LinkedIn Activity API documentation
    <https://docs.agent.ai/api-reference/get-data/get-linkedin-activity>`_.

    Args:
        profile_urls: A list of LinkedIn profile URLs to analyze. Each URL
            must be a fully qualified URL, including ``http://`` or
            ``https://``.
        num_posts: The number of recent posts to fetch from each profile.
            Can be one of:
            - ``1``: 1 post
            - ``5``: 5 posts
            - ``10``: 10 posts
            - ``25``: 25 posts
            - ``50``: 50 posts
            - ``100``: 100 posts

            Defaults to ``3``.

    Returns:
        A dictionary containing the recent LinkedIn posts, including the
        profile URL, post content, and other relevant information.

    Raises:
        ValueError: If the provided profile URLs are invalid.
    """
    endpoint = self.config.endpoints.get_linkedin_activity
    data: dict[str, Any] = {}

    if not isinstance(num_posts, int) or num_posts <= 0:
        raise ValueError("Number of posts must be a positive integer.")

    if not profile_urls:
        raise ValueError("Profile URLs cannot be empty.")

    # validate profile URLs
    try:
        for url in profile_urls:
            parsed_url = urlparse(url)

        # We check for a valid scheme (http/https) and a domain.
        if not (parsed_url.scheme in ["http", "https"] and parsed_url.netloc):
            raise ValueError(
                "URL must have a valid scheme (http/https) and domain name."
            )

    except (ValueError, AttributeError) as e:
        error_message = f"Invalid URL provided: '{url}'"
        await self._logger.error(error_message, url=url)
        raise ValueError(error_message) from e

    data["profile_urls"] = profile_urls
    data["num_posts"] = num_posts

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    response_activity: dict[str, Any] = response_data.get("response", {})

    return response_activity
