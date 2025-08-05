# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.types import (
    IntegrationListResponse,
    IntegrationCreateResponse,
    IntegrationRetrieveResponse,
)
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIntegrations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        integration = client.integrations.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                },
                "integration_type": "s3/v0",
            },
        )
        assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Agility) -> None:
        integration = client.integrations.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                    "resource_type": "s3/v0",
                },
                "integration_category": "rbac",
                "integration_type": "s3/v0",
            },
        )
        assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.integrations.with_raw_response.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                },
                "integration_type": "s3/v0",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.integrations.with_streaming_response.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                },
                "integration_type": "s3/v0",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        integration = client.integrations.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(IntegrationRetrieveResponse, integration, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.integrations.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(IntegrationRetrieveResponse, integration, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.integrations.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(IntegrationRetrieveResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_id` but received ''"):
            client.integrations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        integration = client.integrations.list()
        assert_matches_type(SyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        integration = client.integrations.list(
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.integrations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(SyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.integrations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(SyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Agility) -> None:
        integration = client.integrations.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert integration is None

    @parametrize
    def test_raw_response_delete(self, client: Agility) -> None:
        response = client.integrations.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert integration is None

    @parametrize
    def test_streaming_response_delete(self, client: Agility) -> None:
        with client.integrations.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert integration is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_id` but received ''"):
            client.integrations.with_raw_response.delete(
                "",
            )


class TestAsyncIntegrations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        integration = await async_client.integrations.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                },
                "integration_type": "s3/v0",
            },
        )
        assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAgility) -> None:
        integration = await async_client.integrations.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                    "resource_type": "s3/v0",
                },
                "integration_category": "rbac",
                "integration_type": "s3/v0",
            },
        )
        assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.integrations.with_raw_response.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                },
                "integration_type": "s3/v0",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.integrations.with_streaming_response.create(
            integration_params={
                "resource": {
                    "bucket_name": "bucket_name",
                    "prefix": "prefix",
                },
                "integration_type": "s3/v0",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(IntegrationCreateResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        integration = await async_client.integrations.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(IntegrationRetrieveResponse, integration, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.integrations.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(IntegrationRetrieveResponse, integration, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.integrations.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(IntegrationRetrieveResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_id` but received ''"):
            await async_client.integrations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        integration = await async_client.integrations.list()
        assert_matches_type(AsyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        integration = await async_client.integrations.list(
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.integrations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.integrations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[IntegrationListResponse], integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncAgility) -> None:
        integration = await async_client.integrations.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert integration is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAgility) -> None:
        response = await async_client.integrations.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert integration is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAgility) -> None:
        async with async_client.integrations.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert integration is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_id` but received ''"):
            await async_client.integrations.with_raw_response.delete(
                "",
            )
