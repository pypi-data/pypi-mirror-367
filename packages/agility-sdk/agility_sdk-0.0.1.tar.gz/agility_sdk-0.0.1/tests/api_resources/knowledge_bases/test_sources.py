# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage
from agility.types.knowledge_bases import (
    Source,
    SourceStatusResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSources:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "allow_backward_links": True,
                "allow_external_links": True,
                "exclude_regex": "exclude_regex",
                "ignore_sitemap": True,
                "include_regex": "include_regex",
                "limit": 0,
                "max_depth": 0,
                "name": "web_v0",
                "scrape_options": {
                    "headers": {"foo": "string"},
                    "only_main_content": True,
                    "wait_for": 0,
                },
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
            sync=True,
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.create(
                knowledge_base_id="",
                description="description",
                name="name",
                source_params={
                    "urls": ["string"],
                    "name": "web_v0",
                },
                source_schedule={
                    "cron": "cron",
                    "utc_offset": 0,
                },
            )

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.retrieve(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.retrieve(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.retrieve(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.retrieve(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.retrieve(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_update(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "allow_backward_links": True,
                "allow_external_links": True,
                "exclude_regex": "exclude_regex",
                "ignore_sitemap": True,
                "include_regex": "include_regex",
                "limit": 0,
                "max_depth": 0,
                "name": "web_v0",
                "scrape_options": {
                    "headers": {"foo": "string"},
                    "only_main_content": True,
                    "wait_for": 0,
                },
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
            sync=True,
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.update(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
                description="description",
                name="name",
                source_params={
                    "urls": ["string"],
                    "name": "web_v0",
                },
                source_schedule={
                    "cron": "cron",
                    "utc_offset": 0,
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.update(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                description="description",
                name="name",
                source_params={
                    "urls": ["string"],
                    "name": "web_v0",
                },
                source_schedule={
                    "cron": "cron",
                    "utc_offset": 0,
                },
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncMyOffsetPage[Source], source, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[Source], source, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(SyncMyOffsetPage[Source], source, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(SyncMyOffsetPage[Source], source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.list(
                knowledge_base_id="",
            )

    @parametrize
    def test_method_delete(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.delete(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert source is None

    @parametrize
    def test_raw_response_delete(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.delete(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert source is None

    @parametrize
    def test_streaming_response_delete(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.delete(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert source is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.delete(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.delete(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_status(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.status(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SourceStatusResponse, source, path=["response"])

    @parametrize
    def test_raw_response_status(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.status(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(SourceStatusResponse, source, path=["response"])

    @parametrize
    def test_streaming_response_status(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.status(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(SourceStatusResponse, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_status(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.status(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.status(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_sync(self, client: Agility) -> None:
        source = client.knowledge_bases.sources.sync(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, source, path=["response"])

    @parametrize
    def test_raw_response_sync(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.with_raw_response.sync(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(object, source, path=["response"])

    @parametrize
    def test_streaming_response_sync(self, client: Agility) -> None:
        with client.knowledge_bases.sources.with_streaming_response.sync(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(object, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_sync(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.sync(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.with_raw_response.sync(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncSources:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "allow_backward_links": True,
                "allow_external_links": True,
                "exclude_regex": "exclude_regex",
                "ignore_sitemap": True,
                "include_regex": "include_regex",
                "limit": 0,
                "max_depth": 0,
                "name": "web_v0",
                "scrape_options": {
                    "headers": {"foo": "string"},
                    "only_main_content": True,
                    "wait_for": 0,
                },
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
            sync=True,
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.create(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.create(
                knowledge_base_id="",
                description="description",
                name="name",
                source_params={
                    "urls": ["string"],
                    "name": "web_v0",
                },
                source_schedule={
                    "cron": "cron",
                    "utc_offset": 0,
                },
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.retrieve(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.retrieve(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.retrieve(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.retrieve(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.retrieve(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "allow_backward_links": True,
                "allow_external_links": True,
                "exclude_regex": "exclude_regex",
                "ignore_sitemap": True,
                "include_regex": "include_regex",
                "limit": 0,
                "max_depth": 0,
                "name": "web_v0",
                "scrape_options": {
                    "headers": {"foo": "string"},
                    "only_main_content": True,
                    "wait_for": 0,
                },
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
            sync=True,
        )
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(Source, source, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.update(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            name="name",
            source_params={
                "urls": ["string"],
                "name": "web_v0",
            },
            source_schedule={
                "cron": "cron",
                "utc_offset": 0,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.update(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
                description="description",
                name="name",
                source_params={
                    "urls": ["string"],
                    "name": "web_v0",
                },
                source_schedule={
                    "cron": "cron",
                    "utc_offset": 0,
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.update(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                description="description",
                name="name",
                source_params={
                    "urls": ["string"],
                    "name": "web_v0",
                },
                source_schedule={
                    "cron": "cron",
                    "utc_offset": 0,
                },
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncMyOffsetPage[Source], source, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[Source], source, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[Source], source, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.list(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[Source], source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.list(
                knowledge_base_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.delete(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert source is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.delete(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert source is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.delete(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert source is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.delete(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.delete(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_status(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.status(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SourceStatusResponse, source, path=["response"])

    @parametrize
    async def test_raw_response_status(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.status(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(SourceStatusResponse, source, path=["response"])

    @parametrize
    async def test_streaming_response_status(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.status(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(SourceStatusResponse, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_status(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.status(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.status(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_sync(self, async_client: AsyncAgility) -> None:
        source = await async_client.knowledge_bases.sources.sync(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, source, path=["response"])

    @parametrize
    async def test_raw_response_sync(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.with_raw_response.sync(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(object, source, path=["response"])

    @parametrize
    async def test_streaming_response_sync(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.with_streaming_response.sync(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(object, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_sync(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.sync(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.with_raw_response.sync(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
