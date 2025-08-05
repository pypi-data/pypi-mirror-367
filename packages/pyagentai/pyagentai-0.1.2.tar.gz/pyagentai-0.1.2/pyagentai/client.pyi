# pyagentai/client.pyi
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import httpx

from pyagentai.config.agentai_config import AgentAIConfig
from pyagentai.types.agent_info import AgentInfo
from pyagentai.types.url_endpoint import Endpoint

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])

class AgentAIClient:
    """
    Type stub for AgentAIClient.

    This file provides type hints for static analysis tools like mypy and
    for IDEs like VSCode, allowing them to understand the methods that are
    dynamically attached to the client at runtime.
    """

    # --- Statically defined attributes ---
    config: AgentAIConfig
    _logger: Any

    # --- Statically defined methods ---
    def __init__(
        self,
        api_key: str | None = None,
        config: AgentAIConfig | None = None,
    ) -> None: ...
    async def close(self) -> None: ...

    # --- Internal methods used by registered functions ---
    async def _make_request(
        self, endpoint: Endpoint, data: dict[str, Any] | None = None
    ) -> httpx.Response: ...

    # --- Class methods for dynamic registration ---
    @classmethod
    def register(cls, func: T, *, name: str | None = None) -> T: ...

    # --- Dynamically registered methods ---
    # --- Find Agents ---
    async def find_agents(
        self,
        status: str | None = None,
        slug: str | None = None,
        query: str | None = None,
        tag: str | None = None,
        intent: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AgentInfo]: ...

    # --- Grab Web Text ---
    async def grab_web_text(
        self,
        url: str,
        mode: str = "scrape",
    ) -> tuple[str, dict]: ...

    # --- Grab Web Screenshot ---
    async def grab_web_screenshot(
        self,
        url: str,
        ttl_for_screenshot: int = 3600,
    ) -> str: ...

    # --- Get YouTube Transcript ---
    async def get_youtube_transcript(
        self,
        url: str,
    ) -> tuple[str, dict]: ...

    # --- Get YouTube Channel ---
    async def get_youtube_channel(
        self,
        url: str,
    ) -> dict: ...

    # --- Get Twitter Users ---
    async def get_twitter_users(
        self,
        keywords: str,
        num_users: int = 1,
    ) -> list[str]: ...

    # --- Company Financial Info ---
    async def company_financial_info(
        self,
        company: str,
        quarter: int,
        year: int,
    ) -> str: ...

    # --- Company Financial Profile ---
    async def company_financial_profile(
        self,
        company: str,
    ) -> dict[str, Any]: ...

    # --- Domain Info ---
    async def domain_info(
        self,
        domain: str,
    ) -> dict[str, Any]: ...

    # --- Get Google News ---
    async def get_google_news(
        self,
        query: str,
        date_range: str = "24h",
        location: str | None = None,
    ) -> dict[str, Any]: ...

    # --- Run YouTube Search ---
    async def run_youtube_search(
        self,
        query: str,
    ) -> dict[str, Any]: ...

    # --- Get Search Results ---
    async def get_search_results(
        self,
        query: str,
        search_engine: str = "google",
        num_posts: int = 10,
    ) -> dict[str, Any]: ...

    # --- Get Recent Tweets ---
    async def get_recent_tweets(
        self,
        profile_handle: str,
        recent_tweets_count: int = 1,
    ) -> dict[str, Any]: ...

    # --- Get LinkedIn Profile ---
    async def get_linkedin_profile(
        self,
        profile_handle: str,
    ) -> dict[str, Any]: ...

    # --- Find LinkedIn Profile ---
    async def find_linkedin_profile(
        self,
        query: str,
    ) -> str: ...

    # --- Get LinkedIn Activity ---
    async def get_linkedin_activity(
        self,
        profile_urls: list[str],
        num_posts: int = 3,
    ) -> dict[str, Any]: ...

    # --- Get Company Object ---
    async def get_company_object(
        self,
        domain: str,
    ) -> dict: ...

    # --- Get Bluesky Posts ---
    async def get_bluesky_posts(
        self,
        handle: str,
        num_posts: int = 5,
    ) -> dict[str, Any]: ...

    # --- Search Bluesky Posts ---
    async def search_bluesky_posts(
        self,
        query: str,
        num_posts: int = 1,
    ) -> dict[str, Any]: ...

    # --- Get Instagram Profile ---
    async def get_instagram_profile(
        self,
        username: str,
    ) -> dict[str, Any]: ...

    # --- Get Instagram Followers ---
    async def get_instagram_followers(
        self,
        username: str,
        limit: int = 20,
    ) -> dict[str, Any]: ...
