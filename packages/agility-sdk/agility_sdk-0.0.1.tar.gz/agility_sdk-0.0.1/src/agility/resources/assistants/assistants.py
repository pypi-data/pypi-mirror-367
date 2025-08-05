# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Literal

import httpx

from ...types import assistant_list_params, assistant_create_params, assistant_update_params
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
from .access_keys import (
    AccessKeysResource,
    AsyncAccessKeysResource,
    AccessKeysResourceWithRawResponse,
    AsyncAccessKeysResourceWithRawResponse,
    AccessKeysResourceWithStreamingResponse,
    AsyncAccessKeysResourceWithStreamingResponse,
)
from ...pagination import SyncMyOffsetPage, AsyncMyOffsetPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.assistant import Assistant
from ...types.assistant_with_config import AssistantWithConfig
from ...types.assistant_list_response import AssistantListResponse
from ...types.assistant_retrieve_run_metadata_response import AssistantRetrieveRunMetadataResponse

__all__ = ["AssistantsResource", "AsyncAssistantsResource"]


class AssistantsResource(SyncAPIResource):
    @cached_property
    def access_keys(self) -> AccessKeysResource:
        return AccessKeysResource(self._client)

    @cached_property
    def with_raw_response(self) -> AssistantsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AssistantsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssistantsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AssistantsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: str,
        knowledge_base_id: Optional[str],
        name: str,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: bool | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[assistant_create_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        logo_s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        logo_text: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        suggested_questions: List[str] | NotGiven = NOT_GIVEN,
        url_slug: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Assistant:
        """
        Create a new assistant.

        Args:
          description: The description of the assistant

          name: The name of the assistant

          context_limit: The maximum number of context chunks to include in a run.

          logo_s3_key: S3 object key to the assistant's logo image

          logo_text: Text to display alongside the assistant's logo

          suggested_questions: A list of suggested questions that can be asked to the assistant

          url_slug: Optional URL suffix - unique identifier for the assistant's endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/assistants/",
            body=maybe_transform(
                {
                    "description": description,
                    "knowledge_base_id": knowledge_base_id,
                    "name": name,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "logo_s3_key": logo_s3_key,
                    "logo_text": logo_text,
                    "model": model,
                    "suggested_questions": suggested_questions,
                    "url_slug": url_slug,
                },
                assistant_create_params.AssistantCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Assistant,
        )

    def retrieve(
        self,
        assistant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantWithConfig:
        """
        Get a single assistant by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return self._get(
            f"/api/assistants/{assistant_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistantWithConfig,
        )

    def update(
        self,
        assistant_id: str,
        *,
        id: str,
        description: str,
        knowledge_base_id: Optional[str],
        name: str,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: bool | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[assistant_update_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        logo_s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        logo_text: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        suggested_questions: List[str] | NotGiven = NOT_GIVEN,
        url_slug: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantWithConfig:
        """
        Update an assistant.

        Args:
          description: The description of the assistant

          name: The name of the assistant

          context_limit: The maximum number of context chunks to include in a run.

          logo_s3_key: S3 object key to the assistant's logo image

          logo_text: Text to display alongside the assistant's logo

          suggested_questions: A list of suggested questions that can be asked to the assistant

          url_slug: Optional URL suffix - unique identifier for the assistant's endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return self._put(
            f"/api/assistants/{assistant_id}",
            body=maybe_transform(
                {
                    "id": id,
                    "description": description,
                    "knowledge_base_id": knowledge_base_id,
                    "name": name,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "logo_s3_key": logo_s3_key,
                    "logo_text": logo_text,
                    "model": model,
                    "suggested_questions": suggested_questions,
                    "url_slug": url_slug,
                },
                assistant_update_params.AssistantUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistantWithConfig,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncMyOffsetPage[AssistantListResponse]:
        """
        Get all assistants for the current user.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/assistants/",
            page=SyncMyOffsetPage[AssistantListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    assistant_list_params.AssistantListParams,
                ),
            ),
            model=AssistantListResponse,
        )

    def delete(
        self,
        assistant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete an assistant.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/assistants/{assistant_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_run_metadata(
        self,
        run_id: str,
        *,
        assistant_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantRetrieveRunMetadataResponse:
        """
        Get historical run metadata for an assistant.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get(
            f"/api/assistants/{assistant_id}/historical_run_metadata/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistantRetrieveRunMetadataResponse,
        )


class AsyncAssistantsResource(AsyncAPIResource):
    @cached_property
    def access_keys(self) -> AsyncAccessKeysResource:
        return AsyncAccessKeysResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAssistantsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssistantsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssistantsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AsyncAssistantsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: str,
        knowledge_base_id: Optional[str],
        name: str,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: bool | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[assistant_create_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        logo_s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        logo_text: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        suggested_questions: List[str] | NotGiven = NOT_GIVEN,
        url_slug: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Assistant:
        """
        Create a new assistant.

        Args:
          description: The description of the assistant

          name: The name of the assistant

          context_limit: The maximum number of context chunks to include in a run.

          logo_s3_key: S3 object key to the assistant's logo image

          logo_text: Text to display alongside the assistant's logo

          suggested_questions: A list of suggested questions that can be asked to the assistant

          url_slug: Optional URL suffix - unique identifier for the assistant's endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/assistants/",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "knowledge_base_id": knowledge_base_id,
                    "name": name,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "logo_s3_key": logo_s3_key,
                    "logo_text": logo_text,
                    "model": model,
                    "suggested_questions": suggested_questions,
                    "url_slug": url_slug,
                },
                assistant_create_params.AssistantCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Assistant,
        )

    async def retrieve(
        self,
        assistant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantWithConfig:
        """
        Get a single assistant by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return await self._get(
            f"/api/assistants/{assistant_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistantWithConfig,
        )

    async def update(
        self,
        assistant_id: str,
        *,
        id: str,
        description: str,
        knowledge_base_id: Optional[str],
        name: str,
        codex_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        codex_as_cache: bool | NotGiven = NOT_GIVEN,
        context_limit: Optional[int] | NotGiven = NOT_GIVEN,
        hard_coded_queries: Optional[Iterable[assistant_update_params.HardCodedQuery]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        logo_s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        logo_text: Optional[str] | NotGiven = NOT_GIVEN,
        model: Optional[Literal["gpt-4o"]] | NotGiven = NOT_GIVEN,
        suggested_questions: List[str] | NotGiven = NOT_GIVEN,
        url_slug: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantWithConfig:
        """
        Update an assistant.

        Args:
          description: The description of the assistant

          name: The name of the assistant

          context_limit: The maximum number of context chunks to include in a run.

          logo_s3_key: S3 object key to the assistant's logo image

          logo_text: Text to display alongside the assistant's logo

          suggested_questions: A list of suggested questions that can be asked to the assistant

          url_slug: Optional URL suffix - unique identifier for the assistant's endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return await self._put(
            f"/api/assistants/{assistant_id}",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "description": description,
                    "knowledge_base_id": knowledge_base_id,
                    "name": name,
                    "codex_access_key": codex_access_key,
                    "codex_as_cache": codex_as_cache,
                    "context_limit": context_limit,
                    "hard_coded_queries": hard_coded_queries,
                    "instructions": instructions,
                    "logo_s3_key": logo_s3_key,
                    "logo_text": logo_text,
                    "model": model,
                    "suggested_questions": suggested_questions,
                    "url_slug": url_slug,
                },
                assistant_update_params.AssistantUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistantWithConfig,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AssistantListResponse, AsyncMyOffsetPage[AssistantListResponse]]:
        """
        Get all assistants for the current user.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/assistants/",
            page=AsyncMyOffsetPage[AssistantListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    assistant_list_params.AssistantListParams,
                ),
            ),
            model=AssistantListResponse,
        )

    async def delete(
        self,
        assistant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete an assistant.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/assistants/{assistant_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_run_metadata(
        self,
        run_id: str,
        *,
        assistant_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantRetrieveRunMetadataResponse:
        """
        Get historical run metadata for an assistant.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._get(
            f"/api/assistants/{assistant_id}/historical_run_metadata/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistantRetrieveRunMetadataResponse,
        )


class AssistantsResourceWithRawResponse:
    def __init__(self, assistants: AssistantsResource) -> None:
        self._assistants = assistants

        self.create = to_raw_response_wrapper(
            assistants.create,
        )
        self.retrieve = to_raw_response_wrapper(
            assistants.retrieve,
        )
        self.update = to_raw_response_wrapper(
            assistants.update,
        )
        self.list = to_raw_response_wrapper(
            assistants.list,
        )
        self.delete = to_raw_response_wrapper(
            assistants.delete,
        )
        self.retrieve_run_metadata = to_raw_response_wrapper(
            assistants.retrieve_run_metadata,
        )

    @cached_property
    def access_keys(self) -> AccessKeysResourceWithRawResponse:
        return AccessKeysResourceWithRawResponse(self._assistants.access_keys)


class AsyncAssistantsResourceWithRawResponse:
    def __init__(self, assistants: AsyncAssistantsResource) -> None:
        self._assistants = assistants

        self.create = async_to_raw_response_wrapper(
            assistants.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            assistants.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            assistants.update,
        )
        self.list = async_to_raw_response_wrapper(
            assistants.list,
        )
        self.delete = async_to_raw_response_wrapper(
            assistants.delete,
        )
        self.retrieve_run_metadata = async_to_raw_response_wrapper(
            assistants.retrieve_run_metadata,
        )

    @cached_property
    def access_keys(self) -> AsyncAccessKeysResourceWithRawResponse:
        return AsyncAccessKeysResourceWithRawResponse(self._assistants.access_keys)


class AssistantsResourceWithStreamingResponse:
    def __init__(self, assistants: AssistantsResource) -> None:
        self._assistants = assistants

        self.create = to_streamed_response_wrapper(
            assistants.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            assistants.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            assistants.update,
        )
        self.list = to_streamed_response_wrapper(
            assistants.list,
        )
        self.delete = to_streamed_response_wrapper(
            assistants.delete,
        )
        self.retrieve_run_metadata = to_streamed_response_wrapper(
            assistants.retrieve_run_metadata,
        )

    @cached_property
    def access_keys(self) -> AccessKeysResourceWithStreamingResponse:
        return AccessKeysResourceWithStreamingResponse(self._assistants.access_keys)


class AsyncAssistantsResourceWithStreamingResponse:
    def __init__(self, assistants: AsyncAssistantsResource) -> None:
        self._assistants = assistants

        self.create = async_to_streamed_response_wrapper(
            assistants.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            assistants.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            assistants.update,
        )
        self.list = async_to_streamed_response_wrapper(
            assistants.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            assistants.delete,
        )
        self.retrieve_run_metadata = async_to_streamed_response_wrapper(
            assistants.retrieve_run_metadata,
        )

    @cached_property
    def access_keys(self) -> AsyncAccessKeysResourceWithStreamingResponse:
        return AsyncAccessKeysResourceWithStreamingResponse(self._assistants.access_keys)
