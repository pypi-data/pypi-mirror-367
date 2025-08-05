# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.types import Integration

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRbac:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_verify(self, client: Agility) -> None:
        rbac = client.integrations.rbac.verify(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Integration, rbac, path=["response"])

    @parametrize
    def test_raw_response_verify(self, client: Agility) -> None:
        response = client.integrations.rbac.with_raw_response.verify(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rbac = response.parse()
        assert_matches_type(Integration, rbac, path=["response"])

    @parametrize
    def test_streaming_response_verify(self, client: Agility) -> None:
        with client.integrations.rbac.with_streaming_response.verify(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rbac = response.parse()
            assert_matches_type(Integration, rbac, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_verify(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_id` but received ''"):
            client.integrations.rbac.with_raw_response.verify(
                "",
            )


class TestAsyncRbac:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_verify(self, async_client: AsyncAgility) -> None:
        rbac = await async_client.integrations.rbac.verify(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Integration, rbac, path=["response"])

    @parametrize
    async def test_raw_response_verify(self, async_client: AsyncAgility) -> None:
        response = await async_client.integrations.rbac.with_raw_response.verify(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rbac = await response.parse()
        assert_matches_type(Integration, rbac, path=["response"])

    @parametrize
    async def test_streaming_response_verify(self, async_client: AsyncAgility) -> None:
        async with async_client.integrations.rbac.with_streaming_response.verify(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rbac = await response.parse()
            assert_matches_type(Integration, rbac, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_verify(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `integration_id` but received ''"):
            await async_client.integrations.rbac.with_raw_response.verify(
                "",
            )
