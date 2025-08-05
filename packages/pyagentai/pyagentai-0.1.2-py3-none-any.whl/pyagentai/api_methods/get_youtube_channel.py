from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_youtube_channel(
    self: AgentAIClient,
    url: str,
) -> dict:
    """Retrieve detailed information about a YouTube channel,
    including its videos and statistics.

    For more details, see the `official Get YouTube Channel API documentation
    <https://docs.agent.ai/api-reference/get-data/youtube-channel-data>`_.

    Args:
        url: The URL of the YouTube channel. Must be a fully qualified URL,
            including ``http://`` or ``https://``.

    Returns:
        The channel information as a dictionary of objects.

    Raises:
        ValueError: If the provided URL is invalid.
    """
    endpoint = self.config.endpoints.get_youtube_channel
    data = {}

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

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    channel_info: dict = response_data.get("response", {})

    return channel_info
