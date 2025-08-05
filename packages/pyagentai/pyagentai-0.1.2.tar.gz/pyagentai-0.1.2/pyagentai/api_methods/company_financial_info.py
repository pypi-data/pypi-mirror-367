from typing import Any

from pyagentai.client import AgentAIClient


@AgentAIClient.register
async def company_financial_info(
    self: AgentAIClient,
    company: str,
    quarter: int,
    year: int,
) -> str:
    """
    Retrieve company earnings information for a given stock symbol over time.

    For more details, see the `official Company Earnings Info API documentation
    <https://docs.agent.ai/api-reference/get-data/get-company-earnings-info>`_.

    Args:
        company: The stock symbol of the company.
        quarter: The quarter of the year to retrieve earnings info.
        year: The year of the earnings info to retrieve.

    Returns:
        A string containing the company earnings information.

    Raises:
        ValueError: If the provided parameters are invalid.
    """
    endpoint = self.config.endpoints.company_financial_info
    data: dict[str, Any] = {}

    # validate parameters
    if not company or not company.strip():
        raise ValueError("Company cannot be empty.")

    if not isinstance(quarter, int) or quarter not in [1, 2, 3, 4]:
        raise ValueError("Quarter must be an integer between 1 and 4.")

    if not isinstance(year, int) or year < 2000:
        raise ValueError("Year must be an integer greater than 2000.")

    data["company"] = company.strip().upper()
    data["quarter"] = quarter
    data["year"] = year

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()
    response_text: str = response_data.get("response", "")

    return response_text
