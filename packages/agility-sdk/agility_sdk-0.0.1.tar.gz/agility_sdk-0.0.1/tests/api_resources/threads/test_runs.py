# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.types.threads import Run

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRuns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        run = client.threads.runs.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Agility) -> None:
        run = client.threads.runs.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            additional_instructions="additional_instructions",
            additional_messages=[
                {
                    "content": "content",
                    "metadata": {
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
                    "role": "user",
                    "thread_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
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
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            model="gpt-4o",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.threads.runs.with_raw_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.threads.runs.with_streaming_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.runs.with_raw_response.create(
                thread_id="",
                assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        run = client.threads.runs.retrieve(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.threads.runs.with_raw_response.retrieve(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.threads.runs.with_streaming_response.retrieve(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.runs.with_raw_response.retrieve(
                run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.threads.runs.with_raw_response.retrieve(
                run_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_delete(self, client: Agility) -> None:
        run = client.threads.runs.delete(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert run is None

    @parametrize
    def test_raw_response_delete(self, client: Agility) -> None:
        response = client.threads.runs.with_raw_response.delete(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert run is None

    @parametrize
    def test_streaming_response_delete(self, client: Agility) -> None:
        with client.threads.runs.with_streaming_response.delete(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert run is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.runs.with_raw_response.delete(
                run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.threads.runs.with_raw_response.delete(
                run_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    def test_method_stream(self, client: Agility) -> None:
        run = client.threads.runs.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, run, path=["response"])

    @parametrize
    def test_method_stream_with_all_params(self, client: Agility) -> None:
        run = client.threads.runs.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            additional_instructions="additional_instructions",
            additional_messages=[
                {
                    "content": "content",
                    "metadata": {
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
                    "role": "user",
                    "thread_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
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
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            model="gpt-4o",
        )
        assert_matches_type(object, run, path=["response"])

    @parametrize
    def test_raw_response_stream(self, client: Agility) -> None:
        response = client.threads.runs.with_raw_response.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(object, run, path=["response"])

    @parametrize
    def test_streaming_response_stream(self, client: Agility) -> None:
        with client.threads.runs.with_streaming_response.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(object, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_stream(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.runs.with_raw_response.stream(
                thread_id="",
                assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncRuns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        run = await async_client.threads.runs.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAgility) -> None:
        run = await async_client.threads.runs.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            additional_instructions="additional_instructions",
            additional_messages=[
                {
                    "content": "content",
                    "metadata": {
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
                    "role": "user",
                    "thread_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
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
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            model="gpt-4o",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.runs.with_raw_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.runs.with_streaming_response.create(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.runs.with_raw_response.create(
                thread_id="",
                assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        run = await async_client.threads.runs.retrieve(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.runs.with_raw_response.retrieve(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.runs.with_streaming_response.retrieve(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.runs.with_raw_response.retrieve(
                run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.threads.runs.with_raw_response.retrieve(
                run_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncAgility) -> None:
        run = await async_client.threads.runs.delete(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert run is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.runs.with_raw_response.delete(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert run is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.runs.with_streaming_response.delete(
            run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert run is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.runs.with_raw_response.delete(
                run_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.threads.runs.with_raw_response.delete(
                run_id="",
                thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @parametrize
    async def test_method_stream(self, async_client: AsyncAgility) -> None:
        run = await async_client.threads.runs.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, run, path=["response"])

    @parametrize
    async def test_method_stream_with_all_params(self, async_client: AsyncAgility) -> None:
        run = await async_client.threads.runs.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            additional_instructions="additional_instructions",
            additional_messages=[
                {
                    "content": "content",
                    "metadata": {
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
                    "role": "user",
                    "thread_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
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
            knowledge_base_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            model="gpt-4o",
        )
        assert_matches_type(object, run, path=["response"])

    @parametrize
    async def test_raw_response_stream(self, async_client: AsyncAgility) -> None:
        response = await async_client.threads.runs.with_raw_response.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(object, run, path=["response"])

    @parametrize
    async def test_streaming_response_stream(self, async_client: AsyncAgility) -> None:
        async with async_client.threads.runs.with_streaming_response.stream(
            thread_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(object, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_stream(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.runs.with_raw_response.stream(
                thread_id="",
                assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
