from pyagentai.client import AgentAIClient
from pyagentai.types.agent_info import AgentInfo


@AgentAIClient.register
async def find_agents(
    self: AgentAIClient,
    status: str | None = None,
    slug: str | None = None,
    query: str | None = None,
    tag: str | None = None,
    intent: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AgentInfo]:
    """Search and discover agents on the agent.ai platform.

    This method allows you to find agents by filtering based on their status,
    slug, tags, or by using a search query or a natural language intent.

    For more details, see the official `Find Agents API documentation
    <https://docs.agent.ai/api-reference/agent-discovery/find-agents>`_.

    Args:
        status: Filter agents by visibility status.
            Can be one of ``"public"``, ``"private"``, or ``"any"``.
            Defaults to None.
        slug: Filter agents by their human-readable slug
            (e.g., ``"domainvaluation"``). Defaults to None.
        query: Text to search for in agent names and descriptions.
            Defaults to None.
        tag: Filter agents by a specific tag (e.g., ``"Marketing"``).
            Defaults to None.
        intent: A natural language description of the task you want
            the agent to perform. This helps find agents that match your
            use case. Example: ``"I need to analyze financial statements."``.
            Defaults to None.
        limit: The maximum number of agents to return. Defaults to 50.
            A limit of 0 will return all agents from the offset.
        offset: The offset for pagination. Defaults to 0.

    Returns:
        A list of ``AgentInfo`` objects, each representing an
        agent that matches the search criteria.

    Raises:
        ValueError: If pagination parameters are invalid.
    """
    endpoint = self.config.endpoints.find_agents
    data = {}
    parameters = {
        "status": status,
        "slug": slug,
        "query": query,
        "tag": tag,
        "intent": intent,
    }
    for key, value in parameters.items():
        if value is not None and value.strip():
            data[key] = value.strip().lower()

    # validate pagination parameters
    if offset < 0 or limit < 0:
        await self._logger.error(
            f"Invalid pagination parameters: offset={offset}, limit={limit}"
        )
        return []

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()

    # Extract agents from response
    agents_data: list[dict] = response_data.get("response", [])
    agents = [
        AgentInfo.model_validate(agent_data) for agent_data in agents_data
    ]

    # Apply pagination in memory
    start_idx = min(offset, len(agents))
    end_idx = len(agents) if limit == 0 else min(start_idx + limit, len(agents))

    paginated_agents = agents[start_idx:end_idx]
    log_msg = "Returning %d agents (offset: %d, limit: %d)"
    await self._logger.info(
        log_msg,
        len(paginated_agents),
        offset,
        limit,
    )

    return paginated_agents
