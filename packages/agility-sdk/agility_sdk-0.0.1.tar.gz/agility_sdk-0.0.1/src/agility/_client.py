# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import AgilityError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.users import users
from .resources.threads import threads
from .resources.assistants import assistants
from .resources.integrations import integrations
from .resources.knowledge_bases import knowledge_bases

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Agility",
    "AsyncAgility",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "https://api-agility.cleanlab.ai",
    "staging": "https://api-agility.staging-bc26qf4m.cleanlab.ai",
    "dev": "https://api-agility.dev-bc26qf4m.cleanlab.ai",
    "local": "http://localhost:8080",
}


class Agility(SyncAPIClient):
    assistants: assistants.AssistantsResource
    knowledge_bases: knowledge_bases.KnowledgeBasesResource
    users: users.UsersResource
    threads: threads.ThreadsResource
    integrations: integrations.IntegrationsResource
    with_raw_response: AgilityWithRawResponse
    with_streaming_response: AgilityWithStreamedResponse

    # client options
    bearer_token: str | None
    api_key: str
    access_key: str | None

    _environment: Literal["production", "staging", "dev", "local"] | NotGiven

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        api_key: str | None = None,
        access_key: str | None = None,
        environment: Literal["production", "staging", "dev", "local"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Agility client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `bearer_token` from `BEARER_TOKEN`
        - `api_key` from `AUTHENTICATED_API_KEY`
        - `access_key` from `PUBLIC_ACCESS_KEY`
        """
        if bearer_token is None:
            bearer_token = os.environ.get("BEARER_TOKEN")
        self.bearer_token = bearer_token

        if api_key is None:
            api_key = os.environ.get("AUTHENTICATED_API_KEY")
        if api_key is None:
            raise AgilityError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AUTHENTICATED_API_KEY environment variable"
            )
        self.api_key = api_key

        if access_key is None:
            access_key = os.environ.get("PUBLIC_ACCESS_KEY")
        self.access_key = access_key

        self._environment = environment

        base_url_env = os.environ.get("AGILITY_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `AGILITY_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.assistants = assistants.AssistantsResource(self)
        self.knowledge_bases = knowledge_bases.KnowledgeBasesResource(self)
        self.users = users.UsersResource(self)
        self.threads = threads.ThreadsResource(self)
        self.integrations = integrations.IntegrationsResource(self)
        self.with_raw_response = AgilityWithRawResponse(self)
        self.with_streaming_response = AgilityWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._http_bearer, **self._authenticated_api_key, **self._public_access_key}

    @property
    def _http_bearer(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        if bearer_token is None:
            return {}
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    def _authenticated_api_key(self) -> dict[str, str]:
        api_key = self.api_key
        return {"X-API-Key": api_key}

    @property
    def _public_access_key(self) -> dict[str, str]:
        access_key = self.access_key
        if access_key is None:
            return {}
        return {"X-Access-Key": access_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        api_key: str | None = None,
        access_key: str | None = None,
        environment: Literal["production", "staging", "dev", "local"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            api_key=api_key or self.api_key,
            access_key=access_key or self.access_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncAgility(AsyncAPIClient):
    assistants: assistants.AsyncAssistantsResource
    knowledge_bases: knowledge_bases.AsyncKnowledgeBasesResource
    users: users.AsyncUsersResource
    threads: threads.AsyncThreadsResource
    integrations: integrations.AsyncIntegrationsResource
    with_raw_response: AsyncAgilityWithRawResponse
    with_streaming_response: AsyncAgilityWithStreamedResponse

    # client options
    bearer_token: str | None
    api_key: str
    access_key: str | None

    _environment: Literal["production", "staging", "dev", "local"] | NotGiven

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        api_key: str | None = None,
        access_key: str | None = None,
        environment: Literal["production", "staging", "dev", "local"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncAgility client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `bearer_token` from `BEARER_TOKEN`
        - `api_key` from `AUTHENTICATED_API_KEY`
        - `access_key` from `PUBLIC_ACCESS_KEY`
        """
        if bearer_token is None:
            bearer_token = os.environ.get("BEARER_TOKEN")
        self.bearer_token = bearer_token

        if api_key is None:
            api_key = os.environ.get("AUTHENTICATED_API_KEY")
        if api_key is None:
            raise AgilityError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AUTHENTICATED_API_KEY environment variable"
            )
        self.api_key = api_key

        if access_key is None:
            access_key = os.environ.get("PUBLIC_ACCESS_KEY")
        self.access_key = access_key

        self._environment = environment

        base_url_env = os.environ.get("AGILITY_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `AGILITY_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.assistants = assistants.AsyncAssistantsResource(self)
        self.knowledge_bases = knowledge_bases.AsyncKnowledgeBasesResource(self)
        self.users = users.AsyncUsersResource(self)
        self.threads = threads.AsyncThreadsResource(self)
        self.integrations = integrations.AsyncIntegrationsResource(self)
        self.with_raw_response = AsyncAgilityWithRawResponse(self)
        self.with_streaming_response = AsyncAgilityWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._http_bearer, **self._authenticated_api_key, **self._public_access_key}

    @property
    def _http_bearer(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        if bearer_token is None:
            return {}
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    def _authenticated_api_key(self) -> dict[str, str]:
        api_key = self.api_key
        return {"X-API-Key": api_key}

    @property
    def _public_access_key(self) -> dict[str, str]:
        access_key = self.access_key
        if access_key is None:
            return {}
        return {"X-Access-Key": access_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        api_key: str | None = None,
        access_key: str | None = None,
        environment: Literal["production", "staging", "dev", "local"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            api_key=api_key or self.api_key,
            access_key=access_key or self.access_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AgilityWithRawResponse:
    def __init__(self, client: Agility) -> None:
        self.assistants = assistants.AssistantsResourceWithRawResponse(client.assistants)
        self.knowledge_bases = knowledge_bases.KnowledgeBasesResourceWithRawResponse(client.knowledge_bases)
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.threads = threads.ThreadsResourceWithRawResponse(client.threads)
        self.integrations = integrations.IntegrationsResourceWithRawResponse(client.integrations)


class AsyncAgilityWithRawResponse:
    def __init__(self, client: AsyncAgility) -> None:
        self.assistants = assistants.AsyncAssistantsResourceWithRawResponse(client.assistants)
        self.knowledge_bases = knowledge_bases.AsyncKnowledgeBasesResourceWithRawResponse(client.knowledge_bases)
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.threads = threads.AsyncThreadsResourceWithRawResponse(client.threads)
        self.integrations = integrations.AsyncIntegrationsResourceWithRawResponse(client.integrations)


class AgilityWithStreamedResponse:
    def __init__(self, client: Agility) -> None:
        self.assistants = assistants.AssistantsResourceWithStreamingResponse(client.assistants)
        self.knowledge_bases = knowledge_bases.KnowledgeBasesResourceWithStreamingResponse(client.knowledge_bases)
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.threads = threads.ThreadsResourceWithStreamingResponse(client.threads)
        self.integrations = integrations.IntegrationsResourceWithStreamingResponse(client.integrations)


class AsyncAgilityWithStreamedResponse:
    def __init__(self, client: AsyncAgility) -> None:
        self.assistants = assistants.AsyncAssistantsResourceWithStreamingResponse(client.assistants)
        self.knowledge_bases = knowledge_bases.AsyncKnowledgeBasesResourceWithStreamingResponse(client.knowledge_bases)
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.threads = threads.AsyncThreadsResourceWithStreamingResponse(client.threads)
        self.integrations = integrations.AsyncIntegrationsResourceWithStreamingResponse(client.integrations)


Client = Agility

AsyncClient = AsyncAgility
