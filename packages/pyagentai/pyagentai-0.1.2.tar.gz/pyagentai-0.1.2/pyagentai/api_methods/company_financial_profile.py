from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def company_financial_profile(
    self: AgentAIClient,
    company: str,
) -> dict[str, Any]:
    """
    Retrieve detailed financial and company profile information for a given
    stock symbol, such as market cap and the last known stock price for any
    company.

    For more details, see the `official Company Financial Profile API
    documentation
    <https://docs.agent.ai/api-reference/get-data/get-company-financial-profile>`_.

    Args:
        company: The stock symbol of the company.

    Returns:
        A dictionary containing the company financial profile information.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    endpoint = self.config.endpoints.company_financial_profile
    data: dict[str, Any] = {}

    # validate parameters
    if not company or not company.strip():
        raise ValueError("Company cannot be empty.")

    data["company"] = company.strip().upper()

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    company_data: dict[str, Any] = response_data.get("response", {})

    return company_data
