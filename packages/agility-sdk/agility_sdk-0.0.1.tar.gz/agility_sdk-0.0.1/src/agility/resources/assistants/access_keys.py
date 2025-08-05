# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncMyOffsetPage, AsyncMyOffsetPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.assistants import access_key_list_params, access_key_create_params
from ...types.assistants.access_key import AccessKey

__all__ = ["AccessKeysResource", "AsyncAccessKeysResource"]


class AccessKeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AccessKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AccessKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccessKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AccessKeysResourceWithStreamingResponse(self)

    def create(
        self,
        assistant_id: str,
        *,
        name: str,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        expires_at: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccessKey:
        """
        Creates a new access_key.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return self._post(
            f"/api/assistants/{assistant_id}/access_keys/",
            body=maybe_transform(
                {
                    "name": name,
                    "description": description,
                    "expires_at": expires_at,
                },
                access_key_create_params.AccessKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccessKey,
        )

    def list(
        self,
        assistant_id: str,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncMyOffsetPage[AccessKey]:
        """
        List all access keys for an assistant.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return self._get_api_list(
            f"/api/assistants/{assistant_id}/access_keys/",
            page=SyncMyOffsetPage[AccessKey],
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
                    access_key_list_params.AccessKeyListParams,
                ),
            ),
            model=AccessKey,
        )


class AsyncAccessKeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAccessKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAccessKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccessKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AsyncAccessKeysResourceWithStreamingResponse(self)

    async def create(
        self,
        assistant_id: str,
        *,
        name: str,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        expires_at: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AccessKey:
        """
        Creates a new access_key.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return await self._post(
            f"/api/assistants/{assistant_id}/access_keys/",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "description": description,
                    "expires_at": expires_at,
                },
                access_key_create_params.AccessKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccessKey,
        )

    def list(
        self,
        assistant_id: str,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AccessKey, AsyncMyOffsetPage[AccessKey]]:
        """
        List all access keys for an assistant.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assistant_id:
            raise ValueError(f"Expected a non-empty value for `assistant_id` but received {assistant_id!r}")
        return self._get_api_list(
            f"/api/assistants/{assistant_id}/access_keys/",
            page=AsyncMyOffsetPage[AccessKey],
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
                    access_key_list_params.AccessKeyListParams,
                ),
            ),
            model=AccessKey,
        )


class AccessKeysResourceWithRawResponse:
    def __init__(self, access_keys: AccessKeysResource) -> None:
        self._access_keys = access_keys

        self.create = to_raw_response_wrapper(
            access_keys.create,
        )
        self.list = to_raw_response_wrapper(
            access_keys.list,
        )


class AsyncAccessKeysResourceWithRawResponse:
    def __init__(self, access_keys: AsyncAccessKeysResource) -> None:
        self._access_keys = access_keys

        self.create = async_to_raw_response_wrapper(
            access_keys.create,
        )
        self.list = async_to_raw_response_wrapper(
            access_keys.list,
        )


class AccessKeysResourceWithStreamingResponse:
    def __init__(self, access_keys: AccessKeysResource) -> None:
        self._access_keys = access_keys

        self.create = to_streamed_response_wrapper(
            access_keys.create,
        )
        self.list = to_streamed_response_wrapper(
            access_keys.list,
        )


class AsyncAccessKeysResourceWithStreamingResponse:
    def __init__(self, access_keys: AsyncAccessKeysResource) -> None:
        self._access_keys = access_keys

        self.create = async_to_streamed_response_wrapper(
            access_keys.create,
        )
        self.list = async_to_streamed_response_wrapper(
            access_keys.list,
        )
