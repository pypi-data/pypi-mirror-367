# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agility import Agility, AsyncAgility
from tests.utils import assert_matches_type
from agility._utils import parse_datetime
from agility.pagination import SyncMyOffsetPage, AsyncMyOffsetPage
from agility.types.assistants import AccessKey

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAccessKeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Agility) -> None:
        access_key = client.assistants.access_keys.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(AccessKey, access_key, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Agility) -> None:
        access_key = client.assistants.access_keys.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            description="description",
            expires_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AccessKey, access_key, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Agility) -> None:
        response = client.assistants.access_keys.with_raw_response.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        access_key = response.parse()
        assert_matches_type(AccessKey, access_key, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Agility) -> None:
        with client.assistants.access_keys.with_streaming_response.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            access_key = response.parse()
            assert_matches_type(AccessKey, access_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.assistants.access_keys.with_raw_response.create(
                assistant_id="",
                name="name",
            )

    @parametrize
    def test_method_list(self, client: Agility) -> None:
        access_key = client.assistants.access_keys.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncMyOffsetPage[AccessKey], access_key, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Agility) -> None:
        access_key = client.assistants.access_keys.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(SyncMyOffsetPage[AccessKey], access_key, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Agility) -> None:
        response = client.assistants.access_keys.with_raw_response.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        access_key = response.parse()
        assert_matches_type(SyncMyOffsetPage[AccessKey], access_key, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Agility) -> None:
        with client.assistants.access_keys.with_streaming_response.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            access_key = response.parse()
            assert_matches_type(SyncMyOffsetPage[AccessKey], access_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Agility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.assistants.access_keys.with_raw_response.list(
                assistant_id="",
            )


class TestAsyncAccessKeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncAgility) -> None:
        access_key = await async_client.assistants.access_keys.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(AccessKey, access_key, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAgility) -> None:
        access_key = await async_client.assistants.access_keys.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            description="description",
            expires_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AccessKey, access_key, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.access_keys.with_raw_response.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        access_key = await response.parse()
        assert_matches_type(AccessKey, access_key, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.access_keys.with_streaming_response.create(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            access_key = await response.parse()
            assert_matches_type(AccessKey, access_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await async_client.assistants.access_keys.with_raw_response.create(
                assistant_id="",
                name="name",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAgility) -> None:
        access_key = await async_client.assistants.access_keys.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncMyOffsetPage[AccessKey], access_key, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAgility) -> None:
        access_key = await async_client.assistants.access_keys.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(AsyncMyOffsetPage[AccessKey], access_key, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAgility) -> None:
        response = await async_client.assistants.access_keys.with_raw_response.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        access_key = await response.parse()
        assert_matches_type(AsyncMyOffsetPage[AccessKey], access_key, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAgility) -> None:
        async with async_client.assistants.access_keys.with_streaming_response.list(
            assistant_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            access_key = await response.parse()
            assert_matches_type(AsyncMyOffsetPage[AccessKey], access_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncAgility) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await async_client.assistants.access_keys.with_raw_response.list(
                assistant_id="",
            )
