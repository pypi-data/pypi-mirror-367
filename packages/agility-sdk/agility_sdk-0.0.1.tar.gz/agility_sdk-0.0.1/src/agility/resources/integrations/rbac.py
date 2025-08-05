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
from ...types.integration import Integration

__all__ = ["RbacResource", "AsyncRbacResource"]


class RbacResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RbacResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return RbacResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RbacResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return RbacResourceWithStreamingResponse(self)

    def verify(
        self,
        integration_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Integration:
        """
        Verifies an integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not integration_id:
            raise ValueError(f"Expected a non-empty value for `integration_id` but received {integration_id!r}")
        return self._post(
            f"/api/integrations/rbac/{integration_id}/verify",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Integration,
        )


class AsyncRbacResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRbacResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/agility-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRbacResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRbacResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/agility-python#with_streaming_response
        """
        return AsyncRbacResourceWithStreamingResponse(self)

    async def verify(
        self,
        integration_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Integration:
        """
        Verifies an integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not integration_id:
            raise ValueError(f"Expected a non-empty value for `integration_id` but received {integration_id!r}")
        return await self._post(
            f"/api/integrations/rbac/{integration_id}/verify",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Integration,
        )


class RbacResourceWithRawResponse:
    def __init__(self, rbac: RbacResource) -> None:
        self._rbac = rbac

        self.verify = to_raw_response_wrapper(
            rbac.verify,
        )


class AsyncRbacResourceWithRawResponse:
    def __init__(self, rbac: AsyncRbacResource) -> None:
        self._rbac = rbac

        self.verify = async_to_raw_response_wrapper(
            rbac.verify,
        )


class RbacResourceWithStreamingResponse:
    def __init__(self, rbac: RbacResource) -> None:
        self._rbac = rbac

        self.verify = to_streamed_response_wrapper(
            rbac.verify,
        )


class AsyncRbacResourceWithStreamingResponse:
    def __init__(self, rbac: AsyncRbacResource) -> None:
        self._rbac = rbac

        self.verify = async_to_streamed_response_wrapper(
            rbac.verify,
        )
