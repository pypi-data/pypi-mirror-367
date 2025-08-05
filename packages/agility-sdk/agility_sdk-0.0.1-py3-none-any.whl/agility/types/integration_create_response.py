# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .s3_v0_integration import S3V0Integration
from .gc_sv0_integration import GcSv0Integration

__all__ = [
    "IntegrationCreateResponse",
    "NotionV0Integration",
    "NotionV0IntegrationToken",
    "NotionV0IntegrationTokenNotionAccessToken",
    "NotionV0IntegrationTokenSlackAccessToken",
]


class NotionV0IntegrationTokenNotionAccessToken(BaseModel):
    access_token: str

    bot_id: str

    owner: Dict[str, object]

    workspace_id: str

    integration_type: Optional[Literal["notion/v0"]] = None


class NotionV0IntegrationTokenSlackAccessToken(BaseModel):
    access_token: str

    integration_type: Optional[Literal["slack/v0"]] = None


NotionV0IntegrationToken: TypeAlias = Union[
    NotionV0IntegrationTokenNotionAccessToken, NotionV0IntegrationTokenSlackAccessToken
]


class NotionV0Integration(BaseModel):
    id: str

    token: NotionV0IntegrationToken

    state: Literal["ready", "pending", "error"]

    integration_category: Optional[Literal["rbac", "oauth"]] = None

    integration_type: Optional[Literal["s3/v0", "gcs/v0", "notion/v0", "slack/v0"]] = None


IntegrationCreateResponse: TypeAlias = Union[S3V0Integration, GcSv0Integration, NotionV0Integration]
