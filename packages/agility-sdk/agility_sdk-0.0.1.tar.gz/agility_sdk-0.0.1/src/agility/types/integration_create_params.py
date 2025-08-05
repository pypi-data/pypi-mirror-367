# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "IntegrationCreateParams",
    "IntegrationParams",
    "IntegrationParamsS3IntegrationParamsV0",
    "IntegrationParamsS3IntegrationParamsV0Resource",
    "IntegrationParamsGcsIntegrationParamsV0",
    "IntegrationParamsGcsIntegrationParamsV0Resource",
    "IntegrationParamsNotionIntegrationParamsV0",
]


class IntegrationCreateParams(TypedDict, total=False):
    integration_params: Required[IntegrationParams]
    """S3 integration params model."""


class IntegrationParamsS3IntegrationParamsV0Resource(TypedDict, total=False):
    bucket_name: Required[str]

    prefix: Required[str]

    resource_type: Literal["s3/v0"]


class IntegrationParamsS3IntegrationParamsV0(TypedDict, total=False):
    resource: Required[IntegrationParamsS3IntegrationParamsV0Resource]

    integration_category: Literal["rbac", "oauth"]

    integration_type: Literal["s3/v0"]


class IntegrationParamsGcsIntegrationParamsV0Resource(TypedDict, total=False):
    resource_type: Literal["gcs/v0"]


class IntegrationParamsGcsIntegrationParamsV0(TypedDict, total=False):
    resource: Required[IntegrationParamsGcsIntegrationParamsV0Resource]

    integration_category: Literal["rbac", "oauth"]

    integration_type: Literal["gcs/v0"]


class IntegrationParamsNotionIntegrationParamsV0(TypedDict, total=False):
    authorization_code: Required[str]

    integration_category: Literal["rbac", "oauth"]

    integration_type: Literal["notion/v0"]


IntegrationParams: TypeAlias = Union[
    IntegrationParamsS3IntegrationParamsV0,
    IntegrationParamsGcsIntegrationParamsV0,
    IntegrationParamsNotionIntegrationParamsV0,
]
