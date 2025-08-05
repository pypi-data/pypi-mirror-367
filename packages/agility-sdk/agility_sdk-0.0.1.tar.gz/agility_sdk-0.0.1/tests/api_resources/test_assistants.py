# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.types import (
    Assistant,
    AssistantWithConfig,
    AssistantListResponse,
    AssistantRetrieveRunMetadataResponse,
)
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAssistants:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        assistant = client.assistants.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Agility) -> None:
        assistant = client.assistants.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            codex_access_key="codex_access_key",
            codex_as_cache=True,
            context_limit=1,
            hard_coded_queries=[
                {
                    "query": "query",
                    "response": "response",
                    "context": ["string"],
                    "messages": [{"foo": "bar"}],
                    "prompt": "prompt",
                }
            ],
            instructions="instructions",
            logo_s3_key="logo_s3_key",
            logo_text="logo_text",
            model="gpt-4o",
            suggested_questions=["string"],
            url_slug="url_slug",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.assistants.with_raw_response.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.assistants.with_streaming_response.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        assistant = client.assistants.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.assistants.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.assistants.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(AssistantWithConfig, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.assistants.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Agility) -> None:
        assistant = client.assistants.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Agility) -> None:
        assistant = client.assistants.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            codex_access_key="codex_access_key",
            codex_as_cache=True,
            context_limit=1,
            hard_coded_queries=[
                {
                    "query": "query",
                    "response": "response",
                    "context": ["string"],
                    "messages": [{"foo": "bar"}],
                    "prompt": "prompt",
                }
            ],
            instructions="instructions",
            logo_s3_key="logo_s3_key",
            logo_text="logo_text",
            model="gpt-4o",
            suggested_questions=["string"],
            url_slug="url_slug",
        )
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Agility) -> None:
        response = client.assistants.with_raw_response.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Agility) -> None:
        with client.assistants.with_streaming_response.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(AssistantWithConfig, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.assistants.with_raw_response.update(
                assistant_id="",
                id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                description="description",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                name="name",
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        assistant = client.assistants.list()
        assert_matches_type(SyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        assistant = client.assistants.list(
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.assistants.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(SyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.assistants.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(SyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Agility) -> None:
        assistant = client.assistants.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert assistant is None

    @parametrize
    def test_raw_response_delete(self, client: Agility) -> None:
        response = client.assistants.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert assistant is None

    @parametrize
    def test_streaming_response_delete(self, client: Agility) -> None:
        with client.assistants.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert assistant is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.assistants.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_retrieve_run_metadata(self, client: Agility) -> None:
        assistant = client.assistants.retrieve_run_metadata(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AssistantRetrieveRunMetadataResponse, assistant, path=["response"])

    @parametrize
    def test_raw_response_retrieve_run_metadata(self, client: Agility) -> None:
        response = client.assistants.with_raw_response.retrieve_run_metadata(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(AssistantRetrieveRunMetadataResponse, assistant, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_run_metadata(self, client: Agility) -> None:
        with client.assistants.with_streaming_response.retrieve_run_metadata(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(AssistantRetrieveRunMetadataResponse, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_run_metadata(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.assistants.with_raw_response.retrieve_run_metadata(
                run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                assistant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.assistants.with_raw_response.retrieve_run_metadata(
                run_id="",
                assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncAssistants:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            codex_access_key="codex_access_key",
            codex_as_cache=True,
            context_limit=1,
            hard_coded_queries=[
                {
                    "query": "query",
                    "response": "response",
                    "context": ["string"],
                    "messages": [{"foo": "bar"}],
                    "prompt": "prompt",
                }
            ],
            instructions="instructions",
            logo_s3_key="logo_s3_key",
            logo_text="logo_text",
            model="gpt-4o",
            suggested_questions=["string"],
            url_slug="url_slug",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.with_raw_response.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = await response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.with_streaming_response.create(
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = await response.parse()
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(AssistantWithConfig, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await async_client.assistants.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            codex_access_key="codex_access_key",
            codex_as_cache=True,
            context_limit=1,
            hard_coded_queries=[
                {
                    "query": "query",
                    "response": "response",
                    "context": ["string"],
                    "messages": [{"foo": "bar"}],
                    "prompt": "prompt",
                }
            ],
            instructions="instructions",
            logo_s3_key="logo_s3_key",
            logo_text="logo_text",
            model="gpt-4o",
            suggested_questions=["string"],
            url_slug="url_slug",
        )
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.with_raw_response.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = await response.parse()
        assert_matches_type(AssistantWithConfig, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.with_streaming_response.update(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            description="description",
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(AssistantWithConfig, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await async_client.assistants.with_raw_response.update(
                assistant_id="",
                id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                description="description",
                knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                name="name",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.list()
        assert_matches_type(AsyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.list(
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[AssistantListResponse], assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert assistant is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = await response.parse()
        assert assistant is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert assistant is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await async_client.assistants.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_retrieve_run_metadata(self, async_client: AsyncAgility) -> None:
        assistant = await async_client.assistants.retrieve_run_metadata(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AssistantRetrieveRunMetadataResponse, assistant, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_run_metadata(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.with_raw_response.retrieve_run_metadata(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = await response.parse()
        assert_matches_type(AssistantRetrieveRunMetadataResponse, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_run_metadata(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.with_streaming_response.retrieve_run_metadata(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(AssistantRetrieveRunMetadataResponse, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_run_metadata(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await async_client.assistants.with_raw_response.retrieve_run_metadata(
                run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                assistant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.assistants.with_raw_response.retrieve_run_metadata(
                run_id="",
                assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
