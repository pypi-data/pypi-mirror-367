# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.threads import run_create_params, run_stream_params
from ...types.threads.run import Run

__all__ = ["RunsResource", "AsyncRunsResource"]


class RunsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return RunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return RunsResourceWithStreamingResponse(self)

    def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Iterable[run_create_params.AdditionalMessage] | NotGiven = NOT_GIVEN,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: Optional[bool] | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[run_create_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        knowledge_base_id: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Creates a new run, starting it in the background.

        Args:
          context_limit: The maximum number of context chunks to include.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        return self._post(
            f"/api/threads/{thread_id}/runs/",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "knowledge_base_id": knowledge_base_id,
                    "model": model,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    def retrieve(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Get a run by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get(
            f"/api/threads/{thread_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    def delete(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes a run by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/threads/{thread_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def stream(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Iterable[run_stream_params.AdditionalMessage] | NotGiven = NOT_GIVEN,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: Optional[bool] | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[run_stream_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        knowledge_base_id: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Creates a new run and streams the results.

        Args:
          context_limit: The maximum number of context chunks to include.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        return self._post(
            f"/api/threads/{thread_id}/runs/stream",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "knowledge_base_id": knowledge_base_id,
                    "model": model,
                },
                run_stream_params.RunStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncRunsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AsyncRunsResourceWithStreamingResponse(self)

    async def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Iterable[run_create_params.AdditionalMessage] | NotGiven = NOT_GIVEN,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: Optional[bool] | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[run_create_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        knowledge_base_id: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Creates a new run, starting it in the background.

        Args:
          context_limit: The maximum number of context chunks to include.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        return await self._post(
            f"/api/threads/{thread_id}/runs/",
            body=await async_maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "knowledge_base_id": knowledge_base_id,
                    "model": model,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    async def retrieve(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Get a run by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._get(
            f"/api/threads/{thread_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    async def delete(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes a run by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/threads/{thread_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def stream(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Iterable[run_stream_params.AdditionalMessage] | NotGiven = NOT_GIVEN,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: Optional[bool] | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[run_stream_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        knowledge_base_id: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Creates a new run and streams the results.

        Args:
          context_limit: The maximum number of context chunks to include.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        return await self._post(
            f"/api/threads/{thread_id}/runs/stream",
            body=await async_maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "knowledge_base_id": knowledge_base_id,
                    "model": model,
                },
                run_stream_params.RunStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class RunsResourceWithRawResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.create = to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            runs.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            runs.delete,
        )
        self.stream = to_raw_response_wrapper(
            runs.stream,
        )


class AsyncRunsResourceWithRawResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.create = async_to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            runs.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            runs.delete,
        )
        self.stream = async_to_raw_response_wrapper(
            runs.stream,
        )


class RunsResourceWithStreamingResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.create = to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            runs.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            runs.delete,
        )
        self.stream = to_streamed_response_wrapper(
            runs.stream,
        )


class AsyncRunsResourceWithStreamingResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.create = async_to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            runs.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            runs.delete,
        )
        self.stream = async_to_streamed_response_wrapper(
            runs.stream,
        )
