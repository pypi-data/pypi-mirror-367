# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "Source",
    "SourceParams",
    "SourceParamsWebV0Params",
    "SourceParamsWebV0ParamsScrapeOptions",
    "SourceParamsNotionV0Params",
    "SourceParamsS3PublicV0Params",
    "SourceParamsS3PrivateV0Params",
    "SourceSchedule",
    "Progress",
    "ProgressComplete",
    "ProgressCurate",
    "ProgressLoad",
    "ProgressTransform",
]


class SourceParamsWebV0ParamsScrapeOptions(BaseModel):
    headers: Optional[Dict[str, str]] = None
    """HTTP headers to send with each request.

    Can be used to send cookies, user-agent, etc.
    """

    only_main_content: Optional[bool] = None
    """
    Whether to only scrape the main content of the page (excluding headers, navs,
    footers, etc.).
    """

    wait_for: Optional[int] = None
    """
    Amount of time (in milliseconds) to wait for each page to load before scraping
    content.
    """


class SourceParamsWebV0Params(BaseModel):
    urls: List[str]
    """List of URLs to crawl."""

    allow_backward_links: Optional[bool] = None
    """Whether to allow the crawler to navigate backwards from the given URL."""

    allow_external_links: Optional[bool] = None
    """Whether to allow the crawler to follow links to external websites."""

    exclude_regex: Optional[str] = None
    """Regex pattern to exclude URLs that match the pattern."""

    ignore_sitemap: Optional[bool] = None
    """Whether to ignore the website sitemap when crawling."""

    include_regex: Optional[str] = None
    """Regex pattern to include URLs that match the pattern."""

    limit: Optional[int] = None
    """Maximum number of pages to crawl per URL."""

    max_depth: Optional[int] = None
    """Maximum depth of pages to crawl relative to the root URL."""

    name: Optional[Literal["web_v0"]] = None

    scrape_options: Optional[SourceParamsWebV0ParamsScrapeOptions] = None
    """Parameters for scraping each crawled page."""


class SourceParamsNotionV0Params(BaseModel):
    integration_id: str

    limit: Optional[int] = None

    max_age_days: Optional[int] = None

    name: Optional[Literal["notion_v0"]] = None


class SourceParamsS3PublicV0Params(BaseModel):
    bucket_name: str

    limit: int

    prefix: str

    name: Optional[Literal["s3_public_v0"]] = None


class SourceParamsS3PrivateV0Params(BaseModel):
    bucket_name: str

    integration_id: str

    limit: int

    prefix: str

    name: Optional[Literal["s3_private_v0"]] = None


SourceParams: TypeAlias = Annotated[
    Union[
        SourceParamsWebV0Params, SourceParamsNotionV0Params, SourceParamsS3PublicV0Params, SourceParamsS3PrivateV0Params
    ],
    PropertyInfo(discriminator="name"),
]


class SourceSchedule(BaseModel):
    cron: str

    utc_offset: int


class ProgressComplete(BaseModel):
    processed_documents: Optional[int] = None

    processed_nodes: Optional[int] = None

    result_documents: Optional[int] = None

    result_nodes: Optional[int] = None


class ProgressCurate(BaseModel):
    processed_documents: Optional[int] = None

    processed_nodes: Optional[int] = None

    result_documents: Optional[int] = None

    result_nodes: Optional[int] = None


class ProgressLoad(BaseModel):
    processed_documents: Optional[int] = None

    processed_nodes: Optional[int] = None

    result_documents: Optional[int] = None

    result_nodes: Optional[int] = None


class ProgressTransform(BaseModel):
    processed_documents: Optional[int] = None

    processed_nodes: Optional[int] = None

    result_documents: Optional[int] = None

    result_nodes: Optional[int] = None


class Progress(BaseModel):
    complete: Optional[ProgressComplete] = None
    """Step progress model."""

    curate: Optional[Dict[str, ProgressCurate]] = None

    load: Optional[ProgressLoad] = None
    """Step progress model."""

    transform: Optional[Dict[str, ProgressTransform]] = None


class Source(BaseModel):
    id: str

    created_at: datetime

    deleted_at: Optional[datetime] = None

    description: str

    knowledge_base_id: str

    name: str

    source_params: SourceParams
    """Parameters for web v0 sources."""

    source_schedule: SourceSchedule
    """Source schedule model."""

    status: Literal["pending", "syncing", "synced", "failed"]
    """Source status enum."""

    updated_at: datetime

    progress: Optional[Progress] = None
    """Source progress model."""
