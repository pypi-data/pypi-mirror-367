# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility.types import User

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAPIKey:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Agility) -> None:
        api_key = client.users.api_key.retrieve(
            "user_id",
        )
        assert_matches_type(str, api_key, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Agility) -> None:
        response = client.users.api_key.with_raw_response.retrieve(
            "user_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = response.parse()
        assert_matches_type(str, api_key, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Agility) -> None:
        with client.users.api_key.with_streaming_response.retrieve(
            "user_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = response.parse()
            assert_matches_type(str, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.users.api_key.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_refresh(self, client: Agility) -> None:
        api_key = client.users.api_key.refresh(
            "user_id",
        )
        assert_matches_type(User, api_key, path=["response"])

    @parametrize
    def test_raw_response_refresh(self, client: Agility) -> None:
        response = client.users.api_key.with_raw_response.refresh(
            "user_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = response.parse()
        assert_matches_type(User, api_key, path=["response"])

    @parametrize
    def test_streaming_response_refresh(self, client: Agility) -> None:
        with client.users.api_key.with_streaming_response.refresh(
            "user_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = response.parse()
            assert_matches_type(User, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_refresh(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.users.api_key.with_raw_response.refresh(
                "",
            )


class TestAsyncAPIKey:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgility) -> None:
        api_key = await async_client.users.api_key.retrieve(
            "user_id",
        )
        assert_matches_type(str, api_key, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgility) -> None:
        response = await async_client.users.api_key.with_raw_response.retrieve(
            "user_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = await response.parse()
        assert_matches_type(str, api_key, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgility) -> None:
        async with async_client.users.api_key.with_streaming_response.retrieve(
            "user_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = await response.parse()
            assert_matches_type(str, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.users.api_key.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_refresh(self, async_client: AsyncAgility) -> None:
        api_key = await async_client.users.api_key.refresh(
            "user_id",
        )
        assert_matches_type(User, api_key, path=["response"])

    @parametrize
    async def test_raw_response_refresh(self, async_client: AsyncAgility) -> None:
        response = await async_client.users.api_key.with_raw_response.refresh(
            "user_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = await response.parse()
        assert_matches_type(User, api_key, path=["response"])

    @parametrize
    async def test_streaming_response_refresh(self, async_client: AsyncAgility) -> None:
        async with async_client.users.api_key.with_streaming_response.refresh(
            "user_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = await response.parse()
            assert_matches_type(User, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_refresh(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.users.api_key.with_raw_response.refresh(
                "",
            )
