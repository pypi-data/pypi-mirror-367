# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.integrations.available_list_response import AvailableListResponse

__all__ = ["AvailableResource", "AsyncAvailableResource"]


class AvailableResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AvailableResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AvailableResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AvailableResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AvailableResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AvailableListResponse:
        """Lists available integrations."""
        return self._get(
            "/api/integrations/available",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AvailableListResponse,
        )


class AsyncAvailableResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAvailableResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAvailableResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAvailableResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AsyncAvailableResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AvailableListResponse:
        """Lists available integrations."""
        return await self._get(
            "/api/integrations/available",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AvailableListResponse,
        )


class AvailableResourceWithRawResponse:
    def __init__(self, available: AvailableResource) -> None:
        self._available = available

        self.list = to_raw_response_wrapper(
            available.list,
        )


class AsyncAvailableResourceWithRawResponse:
    def __init__(self, available: AsyncAvailableResource) -> None:
        self._available = available

        self.list = async_to_raw_response_wrapper(
            available.list,
        )


class AvailableResourceWithStreamingResponse:
    def __init__(self, available: AvailableResource) -> None:
        self._available = available

        self.list = to_streamed_response_wrapper(
            available.list,
        )


class AsyncAvailableResourceWithStreamingResponse:
    def __init__(self, available: AsyncAvailableResource) -> None:
        self._available = available

        self.list = async_to_streamed_response_wrapper(
            available.list,
        )
