# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage
from agility.types.knowledge_bases.sources import Document

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        document = client.knowledge_bases.sources.documents.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Document, document, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.documents.with_raw_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(Document, document, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.knowledge_bases.sources.documents.with_streaming_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.documents.with_raw_response.retrieve(
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.documents.with_raw_response.retrieve(
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                source_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.knowledge_bases.sources.documents.with_raw_response.retrieve(
                document_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        document = client.knowledge_bases.sources.documents.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncMyOffsetPage[Document], document, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        document = client.knowledge_bases.sources.documents.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[Document], document, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.knowledge_bases.sources.documents.with_raw_response.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(SyncMyOffsetPage[Document], document, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.knowledge_bases.sources.documents.with_streaming_response.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(SyncMyOffsetPage[Document], document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.sources.documents.with_raw_response.list(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            client.knowledge_bases.sources.documents.with_raw_response.list(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        document = await async_client.knowledge_bases.sources.documents.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Document, document, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.documents.with_raw_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(Document, document, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.documents.with_streaming_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.documents.with_raw_response.retrieve(
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.documents.with_raw_response.retrieve(
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                source_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.knowledge_bases.sources.documents.with_raw_response.retrieve(
                document_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        document = await async_client.knowledge_bases.sources.documents.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncMyOffsetPage[Document], document, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        document = await async_client.knowledge_bases.sources.documents.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[Document], document, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.knowledge_bases.sources.documents.with_raw_response.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[Document], document, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.knowledge_bases.sources.documents.with_streaming_response.list(
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[Document], document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.sources.documents.with_raw_response.list(
                source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `source_id` but received ''"):
            await async_client.knowledge_bases.sources.documents.with_raw_response.list(
                source_id="",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
