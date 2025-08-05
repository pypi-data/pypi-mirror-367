from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def grab_web_text(
    self: AgentAIClient,
    url: str,
    mode: str = "scrape",
) -> tuple[str, dict]:
    """Extract text content from a specified web page or domain.

    This function can be used to either scrape a single page or crawl a
    website up to a certain depth to collect text.

    For more details, see the `official Grab Web Text API documentation
    <https://docs.agent.ai/api-reference/get-data/web-page-content>`_.

    Args:
        url: The URL of the web page to extract text from. Must be a fully
            qualified URL, including ``http://`` or ``https://``.
        mode: The crawler mode. Can be one of:

            - ``"scrape"``: Extracts content from the provided URL only.
            - ``"crawl"``: Crawls the website starting from the URL,
              collecting content from up to 100 pages.

    Returns:
        A tuple containing:

        - The extracted text content as a single string.
        - A dictionary with metadata about the operation.

    Raises:
        ValueError: If the provided URL is invalid.
    """
    endpoint = self.config.endpoints.grab_web_text
    data = {}
    parameters = {
        "url": url,
        "mode": mode,
    }

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

    for key, value in parameters.items():
        if value is not None and value.strip():
            # URL should not be lowercased as the path can be case-sensitive.
            if key == "url":
                data[key] = value.strip()
            else:
                data[key] = value.strip().lower()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()

    # The API returns responses in an unformatted string
    # It contains a metadata JSON and content text
    # TODO: format the response data
    response_text: str = response_data.get("response", "")
    metadata: dict = response_data.get("metadata", {})

    return response_text, metadata
