# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage
from agility.types.threads import Message

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        message = client.threads.messages.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={},
            role="user",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Agility) -> None:
        message = client.threads.messages.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={
                "citations": ["string"],
                "escalated_to_sme": True,
                "guardrailed": True,
                "is_bad_response": True,
                "is_expert_answer": True,
                "original_llm_response": "original_llm_response",
                "scores": {
                    "foo": {
                        "is_bad": True,
                        "log": {"explanation": "explanation"},
                        "score": 0,
                        "triggered": True,
                        "triggered_escalation": True,
                        "triggered_guardrail": True,
                    }
                },
                "trustworthiness_explanation": "trustworthiness_explanation",
                "trustworthiness_score": 0,
            },
            role="user",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.threads.messages.with_raw_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={},
            role="user",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.threads.messages.with_streaming_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={},
            role="user",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.messages.with_raw_response.create(
                thread_id="",
                content="content",
                metadata={},
                role="user",
            )

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        message = client.threads.messages.retrieve(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.threads.messages.with_raw_response.retrieve(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.threads.messages.with_streaming_response.retrieve(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.messages.with_raw_response.retrieve(
                message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.threads.messages.with_raw_response.retrieve(
                message_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        message = client.threads.messages.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncMyOffsetPage[Message], message, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        message = client.threads.messages.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[Message], message, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.threads.messages.with_raw_response.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(SyncMyOffsetPage[Message], message, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.threads.messages.with_streaming_response.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(SyncMyOffsetPage[Message], message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.messages.with_raw_response.list(
                thread_id="",
            )

    @parametrize
    def test_method_delete(self, client: Agility) -> None:
        message = client.threads.messages.delete(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert message is None

    @parametrize
    def test_raw_response_delete(self, client: Agility) -> None:
        response = client.threads.messages.with_raw_response.delete(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert message is None

    @parametrize
    def test_streaming_response_delete(self, client: Agility) -> None:
        with client.threads.messages.with_streaming_response.delete(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert message is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.messages.with_raw_response.delete(
                message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.threads.messages.with_raw_response.delete(
                message_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        message = await async_client.threads.messages.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={},
            role="user",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAgility) -> None:
        message = await async_client.threads.messages.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={
                "citations": ["string"],
                "escalated_to_sme": True,
                "guardrailed": True,
                "is_bad_response": True,
                "is_expert_answer": True,
                "original_llm_response": "original_llm_response",
                "scores": {
                    "foo": {
                        "is_bad": True,
                        "log": {"explanation": "explanation"},
                        "score": 0,
                        "triggered": True,
                        "triggered_escalation": True,
                        "triggered_guardrail": True,
                    }
                },
                "trustworthiness_explanation": "trustworthiness_explanation",
                "trustworthiness_score": 0,
            },
            role="user",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.messages.with_raw_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={},
            role="user",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.messages.with_streaming_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            content="content",
            metadata={},
            role="user",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.messages.with_raw_response.create(
                thread_id="",
                content="content",
                metadata={},
                role="user",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        message = await async_client.threads.messages.retrieve(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.messages.with_raw_response.retrieve(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.messages.with_streaming_response.retrieve(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.messages.with_raw_response.retrieve(
                message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.threads.messages.with_raw_response.retrieve(
                message_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        message = await async_client.threads.messages.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncMyOffsetPage[Message], message, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        message = await async_client.threads.messages.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[Message], message, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.messages.with_raw_response.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[Message], message, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.messages.with_streaming_response.list(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[Message], message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.messages.with_raw_response.list(
                thread_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncAgility) -> None:
        message = await async_client.threads.messages.delete(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert message is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.messages.with_raw_response.delete(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert message is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.messages.with_streaming_response.delete(
            message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert message is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.messages.with_raw_response.delete(
                message_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.threads.messages.with_raw_response.delete(
                message_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
