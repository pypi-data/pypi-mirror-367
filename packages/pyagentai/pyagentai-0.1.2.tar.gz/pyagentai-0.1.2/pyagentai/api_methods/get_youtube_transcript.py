from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_youtube_transcript(
    self: AgentAIClient,
    url: str,
) -> tuple[str, dict]:
    """Fetches the transcript of a YouTube video using the video URL.

    For more details, see the `official Get YouTube Transcript API
    documentation
    <https://docs.agent.ai/api-reference/get-data/youtube-video-transcript>`_.

    Args:
        url: The URL of the YouTube video. Must be a fully qualified URL,
            including ``http://`` or ``https://``.

    Returns:
        A tuple containing:

        - The transcript of the YouTube video as a single string.
        - A dictionary with metadata about the operation.

    Raises:
        ValueError: If the provided URL is invalid.
    """
    endpoint = self.config.endpoints.get_youtube_transcript
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

    response_text: str = response_data.get("response", "")
    metadata: dict = response_data.get("metadata", {})

    return response_text, metadata
