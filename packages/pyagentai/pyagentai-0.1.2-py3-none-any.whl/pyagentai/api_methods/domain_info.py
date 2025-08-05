from typing import Any
from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def domain_info(
    self: AgentAIClient,
    domain: str,
) -> dict[str, Any]:
    """Retrieve detailed information about a domain, including its
    registration details, DNS records, and more.

    For more details, see the `official Domain Info API documentation
    <https://docs.agent.ai/api-reference/get-data/get-domain-information>`_.

    Args:
        domain: The domain name to retrieve information for. Must be a fully
            qualified domain name, including ``http://`` or ``https://``.

    Returns:
        The domain information as a dictionary of objects.

    Raises:
        ValueError: If the provided domain is invalid.
    """
    endpoint = self.config.endpoints.domain_info
    data = {}

    # validate URL
    try:
        parsed_url = urlparse(domain)

        # We check for a valid scheme (http/https) and a domain.
        if not (parsed_url.scheme in ["http", "https"] and parsed_url.netloc):
            raise ValueError(
                "URL must have a valid scheme (http/https) and domain name."
            )

    except (ValueError, AttributeError) as e:
        error_message = f"Invalid domain provided: '{domain}'"
        await self._logger.error(error_message, domain=domain)
        raise ValueError(error_message) from e

    data["domain"] = domain.strip()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    domain_data: dict[str, Any] = response_data.get("response", {})

    return domain_data
