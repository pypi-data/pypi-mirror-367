# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.types import (
    KnowledgeBaseWithConfig,
    KnowledgeBaseListResponse,
)
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestKnowledgeBases:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        knowledge_base = client.knowledge_bases.create(
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {},
            },
            name="name",
        )
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.knowledge_bases.with_raw_response.create(
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {},
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = response.parse()
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.knowledge_bases.with_streaming_response.create(
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {},
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = response.parse()
            assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        knowledge_base = client.knowledge_bases.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.knowledge_bases.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = response.parse()
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.knowledge_bases.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = response.parse()
            assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Agility) -> None:
        knowledge_base = client.knowledge_bases.update(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
            },
            name="name",
        )
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Agility) -> None:
        response = client.knowledge_bases.with_raw_response.update(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = response.parse()
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Agility) -> None:
        with client.knowledge_bases.with_streaming_response.update(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = response.parse()
            assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.with_raw_response.update(
                knowledge_base_id="",
                description="description",
                ingestion_pipeline_params={
                    "curate": {},
                    "curate_document_store": {},
                    "transform": {},
                    "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
                },
                name="name",
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        knowledge_base = client.knowledge_bases.list()
        assert_matches_type(SyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        knowledge_base = client.knowledge_bases.list(
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.knowledge_bases.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = response.parse()
        assert_matches_type(SyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.knowledge_bases.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = response.parse()
            assert_matches_type(SyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Agility) -> None:
        knowledge_base = client.knowledge_bases.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert knowledge_base is None

    @parametrize
    def test_raw_response_delete(self, client: Agility) -> None:
        response = client.knowledge_bases.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = response.parse()
        assert knowledge_base is None

    @parametrize
    def test_streaming_response_delete(self, client: Agility) -> None:
        with client.knowledge_bases.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = response.parse()
            assert knowledge_base is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.with_raw_response.delete(
                "",
            )


class TestAsyncKnowledgeBases:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        knowledge_base = await async_client.knowledge_bases.create(
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {},
            },
            name="name",
        )
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.with_raw_response.create(
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {},
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = await response.parse()
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.with_streaming_response.create(
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {},
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = await response.parse()
            assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        knowledge_base = await async_client.knowledge_bases.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = await response.parse()
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = await response.parse()
            assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncAgility) -> None:
        knowledge_base = await async_client.knowledge_bases.update(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
            },
            name="name",
        )
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.with_raw_response.update(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = await response.parse()
        assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.with_streaming_response.update(
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            ingestion_pipeline_params={
                "curate": {},
                "curate_document_store": {},
                "transform": {},
                "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = await response.parse()
            assert_matches_type(KnowledgeBaseWithConfig, knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.with_raw_response.update(
                knowledge_base_id="",
                description="description",
                ingestion_pipeline_params={
                    "curate": {},
                    "curate_document_store": {},
                    "transform": {},
                    "vector_store": {"weaviate_collection_name": "weaviate_collection_name"},
                },
                name="name",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        knowledge_base = await async_client.knowledge_bases.list()
        assert_matches_type(AsyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        knowledge_base = await async_client.knowledge_bases.list(
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[KnowledgeBaseListResponse], knowledge_base, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncAgility) -> None:
        knowledge_base = await async_client.knowledge_bases.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert knowledge_base is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge_base = await response.parse()
        assert knowledge_base is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge_base = await response.parse()
            assert knowledge_base is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.with_raw_response.delete(
                "",
            )
