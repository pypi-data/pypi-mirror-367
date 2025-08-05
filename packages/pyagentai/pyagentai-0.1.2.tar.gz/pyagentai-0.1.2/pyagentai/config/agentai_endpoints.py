"""Configuration for agent.ai API endpoints."""

from pydantic import BaseModel, Field

from pyagentai.types.url_endpoint import (
    Endpoint,
    EndpointParameter,
    ParameterType,
    RequestMethod,
    UrlType,
)


class AgentAIEndpoints(BaseModel):
    """Endpoints for agent.ai API."""

    find_agents: Endpoint = Field(
        default=Endpoint(
            url="/action/find_agents",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Search and discover agents based on various "
                "criteria including status, tags, and search terms."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="status",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Filter agents by their visibility status.",
                    allowed_values=["any", "public", "private"],
                    validate_parameter=True,
                ),
                EndpointParameter(
                    name="slug",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Filter agents by their human readable slug.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=False,
                    description=(
                        "Text to search for in agent names and descriptions."
                    ),
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="tag",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Filter agents by specific tag.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="intent",
                    param_type=ParameterType.STRING,
                    required=False,
                    description=(
                        "Natural language description of the task "
                        "you want the agent to perform. This helps "
                        "find agents that match your use case."
                    ),
                    validate_parameter=False,
                ),
            ],
        ),
    )

    grab_web_text: Endpoint = Field(
        default=Endpoint(
            url="/action/grab_web_text",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Extract text content from a specified web page or domain."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="url",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="URL of the web page to extract text from.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="mode",
                    param_type=ParameterType.STRING,
                    required=True,
                    description=(
                        "Crawler mode: 'scrape' for one page,"
                        " 'crawl' for up to 100 pages."
                    ),
                    allowed_values=["scrape", "crawl"],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    grab_web_screenshot: Endpoint = Field(
        default=Endpoint(
            url="/action/grab_web_screenshot",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Capture a visual screenshot of a specified web page for "
                "documentation or analysis."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="url",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="URL of the web page to capture.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="ttl_for_screenshot",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description=(
                        "Cache expiration time for the screenshot in seconds."
                    ),
                    allowed_values=[3600, 86400, 604800, 18144000],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    get_youtube_transcript: Endpoint = Field(
        default=Endpoint(
            url="/action/get_youtube_transcript",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Fetches the transcript of a YouTube video using"
                " the video URL."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="url",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="URL of the YouTube video.",
                    validate_parameter=False,
                )
            ],
        ),
    )

    get_youtube_channel: Endpoint = Field(
        default=Endpoint(
            url="/action/get_youtube_channel",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve detailed information about a YouTube channel,"
                " including its videos and statistics."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="url",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="URL of the YouTube channel.",
                    validate_parameter=False,
                )
            ],
        ),
    )

    get_twitter_users: Endpoint = Field(
        default=Endpoint(
            url="/action/get_twitter_users",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Search and retrieve Twitter user profiles based on"
                " specific keywords for targeted social media analysis."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="keywords",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Keywords to find relevant Twitter users.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="num_users",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description="Number of user profiles to retrieve.",
                    allowed_values=[1, 5, 10, 25, 50, 100],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    company_financial_info: Endpoint = Field(
        default=Endpoint(
            url="/action/company_financial_info",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve company earnings information for a "
                "given stock symbol over time."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="company",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol of the company.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="quarter",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description=(
                        "Quarter of the year to retrieve earnings info."
                    ),
                    allowed_values=[1, 2, 3, 4],
                    validate_parameter=True,
                ),
                EndpointParameter(
                    name="year",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description="Year of the earnings info to retrieve.",
                    validate_parameter=False,
                ),
            ],
        ),
    )

    company_financial_profile: Endpoint = Field(
        default=Endpoint(
            url="/action/company_financial_profile",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve detailed financial and company profile information "
                "for a given stock symbol, such as market cap and the last "
                "known stock price for any company."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="company",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol of the company.",
                    validate_parameter=False,
                )
            ],
        ),
    )

    domain_info: Endpoint = Field(
        default=Endpoint(
            url="/action/domain_info",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve detailed information about a domain, including its "
                "registration details, DNS records, and more."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="domain",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Domain name to retrieve information for.",
                    validate_parameter=False,
                )
            ],
        ),
    )

    get_google_news: Endpoint = Field(
        default=Endpoint(
            url="/action/get_google_news",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Fetch news articles based on queries and date ranges to stay "
                "updated on relevant topics or trends."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Search terms to find news articles.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="date_range",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Timeframe for news articles.",
                    allowed_values=["24h", "7d", "30d", "90d"],
                    validate_parameter=True,
                ),
                EndpointParameter(
                    name="location",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Location to filter news results.",
                    validate_parameter=False,
                ),
            ],
        ),
    )

    run_youtube_search: Endpoint = Field(
        default=Endpoint(
            url="/action/run_youtube_search",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Perform a YouTube search and retrieve results for specified "
                "queries."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Search terms for YouTube.",
                    validate_parameter=False,
                ),
            ],
        ),
    )

    get_search_results: Endpoint = Field(
        default=Endpoint(
            url="/action/get_search_results",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Fetch search results from Google or YouTube for specific "
                "queries, providing valuable insights and content."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="search_engine",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Search engine to use.",
                    allowed_values=["google", "youtube", "youtube_channel"],
                    validate_parameter=True,
                ),
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Search terms to find specific results.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="num_posts",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description="Number of results to return.",
                    allowed_values=[1, 5, 10, 25, 50, 100],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    get_recent_tweets: Endpoint = Field(
        default=Endpoint(
            url="/action/get_recent_tweets",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "This action fetches recent tweets from a specified Twitter "
                "handle."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="profile_handle",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Twitter handle to fetch recent tweets from.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="recent_tweets_count",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Number of tweets to return.",
                    validate_parameter=False,
                ),
            ],
        ),
    )

    get_linkedin_profile: Endpoint = Field(
        default=Endpoint(
            url="/action/get_linkedin_profile",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve detailed information from a specified LinkedIn "
                "profile for professional insights."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="profile_handle",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="LinkedIn profile handle to retrieve details.",
                    validate_parameter=False,
                ),
            ],
        ),
    )

    find_linkedin_profile: Endpoint = Field(
        default=Endpoint(
            url="/action/find_linkedin_profile",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=("Find the LinkedIn profile slug for a person."),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=True,
                    description=(
                        "Text query to find the LinkedIn profile slug."
                    ),
                    validate_parameter=False,
                ),
            ],
        ),
    )

    get_linkedin_activity: Endpoint = Field(
        default=Endpoint(
            url="/action/get_linkedin_activity",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve recent LinkedIn posts from specified profiles to "
                "analyze professional activity and engagement."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="profile_urls",
                    param_type=ParameterType.ARRAY,
                    required=True,
                    description="A list of LinkedIn profile URLs.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="num_posts",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description=(
                        "Number of recent posts to fetch from each profile."
                    ),
                    allowed_values=[1, 5, 10, 25, 50, 100],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    get_company_object: Endpoint = Field(
        default=Endpoint(
            url="/action/get_company_object",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Gather enriched company data using Breeze Intelligence for "
                "deeper analysis and insights."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="domain",
                    param_type=ParameterType.STRING,
                    required=True,
                    description=(
                        "Domain of the company to retrieve enriched data."
                    ),
                    validate_parameter=False,
                ),
            ],
        ),
    )

    get_bluesky_posts: Endpoint = Field(
        default=Endpoint(
            url="/action/get_bluesky_posts",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Fetch recent posts from a specified Bluesky user handle, "
                "making it easy to monitor activity on the platform."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="handle",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Bluesky handle to fetch posts from.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="num_posts",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description="Number of posts to return.",
                    allowed_values=[1, 5, 10, 25, 50, 100],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    search_bluesky_posts: Endpoint = Field(
        default=Endpoint(
            url="/action/search_bluesky_posts",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Search for Bluesky posts matching specific keywords or "
                "criteria to gather social media insights."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Search terms to find relevant Bluesky posts.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="num_posts",
                    param_type=ParameterType.INTEGER,
                    required=True,
                    description="Number of matching posts to fetch.",
                    allowed_values=[1, 5, 10, 25, 50, 100],
                    validate_parameter=True,
                ),
            ],
        ),
    )

    get_instagram_profile: Endpoint = Field(
        default=Endpoint(
            url="/action/get_instagram_profile",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Fetch detailed profile information for a specified Instagram "
                "username."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="username",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Instagram username (without @).",
                    validate_parameter=False,
                ),
            ],
        ),
    )

    get_instagram_followers: Endpoint = Field(
        default=Endpoint(
            url="/action/get_instagram_followers",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Retrieve a list of top followers from a specified Instagram "
                "account for social media analysis."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="username",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Instagram username (without @).",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="limit",
                    param_type=ParameterType.STRING,
                    required=True,
                    description="Number of top followers to retrieve.",
                    allowed_values=["10", "20", "50", "100"],
                    validate_parameter=True,
                ),
            ],
        ),
    )
