from typing import Any
from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def grab_web_screenshot(
    self: AgentAIClient,
    url: str,
    ttl_for_screenshot: int = 3600,
) -> str:
    """Capture a visual screenshot of a specified web page for documentation or
    analysis.

    For more details, see the `official Grab Web Screenshot API documentation
    <https://docs.agent.ai/api-reference/get-data/web-page-screenshot>`_.

    Args:
        url: The URL of the web page to capture. Must be a fully
            qualified URL, including ``http://`` or ``https://``.
        ttl_for_screenshot: The cache expiration time for the screenshot in
            seconds. Can be one of:
            - ``3600``: 1 hour
            - ``86400``: 1 day
            - ``604800``: 1 week
            - ``18144000``: 6 months

            Defaults to ``3600``.

    Returns:
        A URL to the screenshot.

    Raises:
        ValueError: If the provided URL is invalid.
    """
    endpoint = self.config.endpoints.grab_web_screenshot
    data: dict[str, Any] = {}

    # validate URL
    try:
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

    data["url"] = url
    data["ttl_for_screenshot"] = ttl_for_screenshot

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()

    # The API returns a URL to the screenshot
    response_url: str = response_data.get("response", "")

    return response_url
