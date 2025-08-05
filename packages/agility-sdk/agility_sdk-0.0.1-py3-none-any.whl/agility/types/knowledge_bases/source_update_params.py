# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "SourceUpdateParams",
    "SourceParams",
    "SourceParamsWebV0Params",
    "SourceParamsWebV0ParamsScrapeOptions",
    "SourceParamsNotionV0Params",
    "SourceParamsS3PublicV0Params",
    "SourceParamsS3PrivateV0Params",
    "SourceSchedule",
]


class SourceUpdateParams(TypedDict, total=False):
    knowledge_base_id: Required[str]

    description: Required[str]

    name: Required[str]

    source_params: Required[SourceParams]
    """Parameters for web v0 sources."""

    source_schedule: Required[SourceSchedule]
    """Source schedule model."""

    sync: bool


class SourceParamsWebV0ParamsScrapeOptions(TypedDict, total=False):
    headers: Dict[str, str]
    """HTTP headers to send with each request.

    Can be used to send cookies, user-agent, etc.
    """

    only_main_content: bool
    """
    Whether to only scrape the main content of the page (excluding headers, navs,
    footers, etc.).
    """

    wait_for: int
    """
    Amount of time (in milliseconds) to wait for each page to load before scraping
    content.
    """


class SourceParamsWebV0Params(TypedDict, total=False):
    urls: Required[List[str]]
    """List of URLs to crawl."""

    allow_backward_links: bool
    """Whether to allow the crawler to navigate backwards from the given URL."""

    allow_external_links: bool
    """Whether to allow the crawler to follow links to external websites."""

    exclude_regex: Optional[str]
    """Regex pattern to exclude URLs that match the pattern."""

    ignore_sitemap: bool
    """Whether to ignore the website sitemap when crawling."""

    include_regex: Optional[str]
    """Regex pattern to include URLs that match the pattern."""

    limit: int
    """Maximum number of pages to crawl per URL."""

    max_depth: int
    """Maximum depth of pages to crawl relative to the root URL."""

    name: Literal["web_v0"]

    scrape_options: SourceParamsWebV0ParamsScrapeOptions
    """Parameters for scraping each crawled page."""


class SourceParamsNotionV0Params(TypedDict, total=False):
    integration_id: Required[str]

    limit: Optional[int]

    max_age_days: int

    name: Literal["notion_v0"]


class SourceParamsS3PublicV0Params(TypedDict, total=False):
    bucket_name: Required[str]

    limit: Required[int]

    prefix: Required[str]

    name: Literal["s3_public_v0"]


class SourceParamsS3PrivateV0Params(TypedDict, total=False):
    bucket_name: Required[str]

    integration_id: Required[str]

    limit: Required[int]

    prefix: Required[str]

    name: Literal["s3_private_v0"]


SourceParams: TypeAlias = Union[
    SourceParamsWebV0Params, SourceParamsNotionV0Params, SourceParamsS3PublicV0Params, SourceParamsS3PrivateV0Params
]


class SourceSchedule(TypedDict, total=False):
    cron: Required[str]

    utc_offset: Required[int]
