from urllib.parse import urlparse

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def get_company_object(
    self: AgentAIClient,
    domain: str,
) -> dict:
    """Gather enriched company data using Breeze Intelligence for deeper
    analysis and insights.

    For more details, see the `official Get Company Object API documentation
    <https://docs.agent.ai/api-reference/get-data/enrich-company-data>`_.

    Args:
        domain: The domain of the company to retrieve enriched data. Must be
            a fully qualified domain name, including ``http://`` or
            ``https://``.

    Returns:
        The company information as a dictionary of objects.

    Raises:
        ValueError: If the provided domain is invalid.
    """
    endpoint = self.config.endpoints.get_company_object
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

    data["domain"] = domain

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    company_info: dict = response_data.get("response", {})

    return company_info
