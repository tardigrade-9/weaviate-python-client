from __future__ import annotations

import asyncio
import os
import socket
import time

from threading import Thread, Event
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING, cast

from httpx import AsyncClient, ConnectError, HTTPError, ReadTimeout, Response, Timeout, get
from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client  # type: ignore

from weaviate.auth import (
    AuthCredentials,
    AuthClientPassword,
    AuthBearerToken,
    AuthClientCredentials,
    AuthApiKey,
)
from weaviate.config import ConnectionConfig
from weaviate.connect.base import _ConnectionBase
from weaviate.embedded import EmbeddedDB
from weaviate.exceptions import (
    MissingScopeException,
    AuthenticationFailedException,
    WeaviateStartUpError,
)
from weaviate.util import _check_positive_num, _decode_json_response_dict, is_weaviate_domain
from weaviate.warnings import _Warnings

try:
    from proto.v1 import weaviate_pb2_grpc

    has_grpc = True

except ImportError:
    has_grpc = False

if TYPE_CHECKING:
    from .connection import ConnectionParams, JSONPayload

AUTH_DEFAULT_TIMEOUT = 5
OIDC_CONFIG = Dict[str, Union[str, List[str]]]


class _Auth:
    def __init__(
        self,
        oidc_config: OIDC_CONFIG,
        credentials: AuthCredentials,
        connection: _ConnectionBase,
    ) -> None:
        self._credentials: AuthCredentials = credentials
        self._connection: _ConnectionBase = connection
        config_url = oidc_config["href"]
        client_id = oidc_config["clientId"]
        assert isinstance(config_url, str) and isinstance(client_id, str)
        self._open_id_config_url: str = config_url
        self._client_id: str = client_id
        self._default_scopes: List[str] = []
        if "scopes" in oidc_config:
            default_scopes = oidc_config["scopes"]
            assert isinstance(default_scopes, list)
            self._default_scopes = default_scopes

        self._token_endpoint: str = self._get_token_endpoint()
        self._validate(oidc_config)

    def _validate(self, oidc_config: OIDC_CONFIG) -> None:
        if isinstance(self._credentials, AuthClientPassword):
            if self._token_endpoint.startswith("https://login.microsoftonline.com"):
                raise AuthenticationFailedException(
                    """Microsoft/azure does not recommend to authenticate using username and password and this method is
                    not supported by the python client."""
                )

            # The grant_types_supported field is optional and does not have to be present in the response
            if (
                "grant_types_supported" in oidc_config
                and "password" not in oidc_config["grant_types_supported"]
            ):
                raise AuthenticationFailedException(
                    """The grant_types supported by the third-party authentication service are insufficient. Please add
                    the 'password' grant type."""
                )

    def _get_token_endpoint(self) -> str:
        response_auth = get(self._open_id_config_url, proxies=self._connection.get_proxies())
        response_auth_json = _decode_json_response_dict(response_auth, "Get token endpoint")
        assert response_auth_json is not None
        token_endpoint = response_auth_json["token_endpoint"]
        assert isinstance(token_endpoint, str)
        return token_endpoint

    def get_sync_auth_client(self) -> OAuth2Client:
        if isinstance(self._credentials, AuthBearerToken):
            session = self._get_client_auth_bearer_token(self._credentials)
        elif isinstance(self._credentials, AuthClientCredentials):
            session = self._get_client_client_credential(self._credentials)
        else:
            assert isinstance(self._credentials, AuthClientPassword)
            session = self._get_client_user_pw(self._credentials)

        return session

    async def get_async_auth_client(self) -> AsyncOAuth2Client:
        if isinstance(self._credentials, AuthBearerToken):
            session = await self._get_aclient_auth_bearer_token(self._credentials)
        elif isinstance(self._credentials, AuthClientCredentials):
            session = await self._get_aclient_client_credential(self._credentials)
        else:
            assert isinstance(self._credentials, AuthClientPassword)
            session = await self._get_aclient_user_pw(self._credentials)

        return session

    def _get_client_auth_bearer_token(self, config: AuthBearerToken) -> OAuth2Client:
        token: Dict[str, Union[str, int]] = {"access_token": config.access_token}
        if config.expires_in is not None:
            token["expires_in"] = config.expires_in
        if config.refresh_token is not None:
            token["refresh_token"] = config.refresh_token

        if "refresh_token" not in token:
            _Warnings.auth_no_refresh_token(config.expires_in)

        # token endpoint and clientId are needed for token refresh
        return OAuth2Client(
            token=token,
            token_endpoint=self._token_endpoint,
            client_id=self._client_id,
            default_timeout=AUTH_DEFAULT_TIMEOUT,
        )

    def _get_aclient_auth_bearer_token(self, config: AuthBearerToken) -> AsyncOAuth2Client:
        token: Dict[str, Union[str, int]] = {"access_token": config.access_token}
        if config.expires_in is not None:
            token["expires_in"] = config.expires_in
        if config.refresh_token is not None:
            token["refresh_token"] = config.refresh_token

        if "refresh_token" not in token:
            _Warnings.auth_no_refresh_token(config.expires_in)

        # token endpoint and clientId are needed for token refresh
        return AsyncOAuth2Client(
            token=token,
            token_endpoint=self._token_endpoint,
            client_id=self._client_id,
            default_timeout=AUTH_DEFAULT_TIMEOUT,
        )

    def _get_client_user_pw(self, config: AuthClientPassword) -> OAuth2Client:
        scope: List[str] = self._default_scopes.copy()
        scope.extend(config.scope_list)
        session = OAuth2Client(
            client_id=self._client_id,
            token_endpoint=self._token_endpoint,
            grant_type="password",
            scope=scope,
            default_timeout=AUTH_DEFAULT_TIMEOUT,
        )
        token = session.fetch_token(username=config.username, password=config.password)
        if "refresh_token" not in token:
            _Warnings.auth_no_refresh_token(token["expires_in"])

        return session

    async def _get_aclient_user_pw(self, config: AuthClientPassword) -> AsyncOAuth2Client:
        scope: List[str] = self._default_scopes.copy()
        scope.extend(config.scope_list)
        session = AsyncOAuth2Client(
            client_id=self._client_id,
            token_endpoint=self._token_endpoint,
            grant_type="password",
            scope=scope,
            default_timeout=AUTH_DEFAULT_TIMEOUT,
        )
        token = await session._fetch_token(username=config.username, password=config.password)
        if "refresh_token" not in token:
            _Warnings.auth_no_refresh_token(token["expires_in"])

        return session

    def _get_client_client_credential(self, config: AuthClientCredentials) -> OAuth2Client:
        scope: List[str] = self._default_scopes.copy()

        if config.scope_list is not None:
            scope.extend(config.scope_list)
        if len(scope) == 0:
            # hardcode commonly used scopes
            if self._token_endpoint.startswith("https://login.microsoftonline.com"):
                scope = [self._client_id + "/.default"]
            else:
                raise MissingScopeException

        session = OAuth2Client(
            client_id=self._client_id,
            client_secret=config.client_secret,
            token_endpoint_auth_method="client_secret_post",
            scope=scope,
            token_endpoint=self._token_endpoint,
            grant_type="client_credentials",
            token={"access_token": None, "expires_in": -100},
            default_timeout=AUTH_DEFAULT_TIMEOUT,
        )
        # explicitly fetch tokens. Otherwise, authlib will do it in the background and we might have race-conditions
        session.fetch_token()
        return session

    async def _get_aclient_client_credential(
        self, config: AuthClientCredentials
    ) -> AsyncOAuth2Client:
        scope: List[str] = self._default_scopes.copy()

        if config.scope_list is not None:
            scope.extend(config.scope_list)
        if len(scope) == 0:
            # hardcode commonly used scopes
            if self._token_endpoint.startswith("https://login.microsoftonline.com"):
                scope = [self._client_id + "/.default"]
            else:
                raise MissingScopeException

        session = AsyncOAuth2Client(
            client_id=self._client_id,
            client_secret=config.client_secret,
            token_endpoint_auth_method="client_secret_post",
            scope=scope,
            token_endpoint=self._token_endpoint,
            grant_type="client_credentials",
            token={"access_token": None, "expires_in": -100},
            default_timeout=AUTH_DEFAULT_TIMEOUT,
        )
        # explicitly fetch tokens. Otherwise, authlib will do it in the background and we might have race-conditions
        await session._fetch_token()
        return session


class ConnectionAsync(_ConnectionBase):
    """
    Connection class used to communicate to a weaviate instance.
    """

    def __init__(
        self,
        connection_params: ConnectionParams,
        auth_client_secret: Optional[AuthCredentials],
        timeout_config: Tuple[float, float],
        proxies: Union[dict, str, None],
        trust_env: bool,
        additional_headers: Optional[Dict[str, Any]],
        startup_period: Optional[int],
        connection_config: ConnectionConfig,
        embedded_db: Optional[EmbeddedDB] = None,
    ):
        self.url = connection_params._http_url
        self.embedded_db = embedded_db
        self._api_version_path = "/v1"
        self._client: AsyncOAuth2Client
        self.__additional_headers = {}
        self.__auth = auth_client_secret
        self.__connection_params = connection_params
        self._grpc_available = False
        self._grpc_stub: Optional[weaviate_pb2_grpc.WeaviateStub] = None
        self.__startup_period = startup_period
        self.__timeout_config = timeout_config

        self._headers = {"content-type": "application/json"}
        if additional_headers is not None:
            if not isinstance(additional_headers, dict):
                raise TypeError(
                    f"'additional_headers' must be of type dict or None. Given type: {type(additional_headers)}."
                )
            self.__additional_headers = additional_headers
            for key, value in additional_headers.items():
                self._headers[key.lower()] = value

        self._proxies = _get_proxies(proxies, trust_env)

        # auth secrets can contain more information than a header (refresh tokens and lifetime) and therefore take
        # precedent over headers
        if "authorization" in self._headers and auth_client_secret is not None:
            _Warnings.auth_header_and_auth_secret()
            self._headers.pop("authorization")

        # if there are API keys included add them right away to headers
        if auth_client_secret is not None and isinstance(auth_client_secret, AuthApiKey):
            self._headers["authorization"] = "Bearer " + auth_client_secret.api_key

    async def connect(self) -> None:
        if self.__startup_period is not None:
            _check_positive_num(self.__startup_period, "startup_period", int, include_zero=False)
            await self.wait_for_weaviate(self.__startup_period)

        loop = asyncio.get_running_loop()
        if has_grpc and self.__connection_params._has_grpc:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(False)
            try:
                s.settimeout(1.0)  # we're only pinging the port, 1s is plenty
                assert self.__connection_params._grpc_address is not None
                await loop.sock_connect(s, (self.__connection_params._grpc_address))
                s.shutdown(2)
                s.close()
                grpc_channel = self.__connection_params._grpc_channel("async")
                assert grpc_channel is not None
                self._grpc_stub = weaviate_pb2_grpc.WeaviateStub(grpc_channel)
                self._grpc_available = True
            except (
                ConnectionRefusedError,
                TimeoutError,
                socket.timeout,
            ):  # self._grpc_stub stays None
                s.close()
                self._grpc_available = False
        await self._create_client(self.__auth)

    def __make_client(self) -> AsyncClient:
        return AsyncClient(
            headers=self._get_request_header(),
            proxies=self._proxies,
            timeout=Timeout(connect=self.__timeout_config[0], read=self.__timeout_config[1]),
        )

    async def _create_client(self, auth_client_secret: Optional[AuthCredentials]) -> None:
        """Creates an async httpx client.

        Either through authlib.oauth2 if authentication is enabled or a normal httpx async client otherwise.

        Raises
        ------
        ValueError
            If no authentication credentials provided but the Weaviate server has OpenID configured.
        """
        # API keys are separate from OIDC and do not need any config from weaviate
        if auth_client_secret is not None and isinstance(auth_client_secret, AuthApiKey):
            self._client = self.__make_client()
            return

        if "authorization" in self._headers and auth_client_secret is None:
            self._client = self.__make_client()
            return

        oidc_url = self.url + self._api_version_path + "/.well-known/openid-configuration"
        async with self.__make_client() as client:
            response = await client.get(
                oidc_url,
            )
        if response.status_code == 200:
            # Some setups are behind proxies that return some default page - for example a login - for all requests.
            # If the response is not json, we assume that this is the case and try unauthenticated access. Any auth
            # header provided by the user is unaffected.
            try:
                resp = response.json()
            except Exception:
                _Warnings.auth_cannot_parse_oidc_config(oidc_url)
                self._client = self.__make_client()
                return

            if auth_client_secret is not None and not isinstance(auth_client_secret, AuthApiKey):
                _auth = _Auth(resp, auth_client_secret, self)
                self._client = await _auth.get_async_auth_client()
            else:
                msg = f""""No login credentials provided. The weaviate instance at {self.url} requires login credentials.

                    Please check our documentation at https://weaviate.io/developers/weaviate/client-libraries/python#authentication
                    for more information about how to use authentication."""

                if is_weaviate_domain(self.url):
                    msg += """

                    You can instantiate the client with login credentials for WCS using

                    client = weaviate.Client(
                      url=YOUR_WEAVIATE_URL,
                      auth_client_secret=weaviate.AuthClientPassword(
                        username = YOUR_WCS_USER,
                        password = YOUR_WCS_PW,
                      ))
                    """
                raise AuthenticationFailedException(msg)
        elif response.status_code == 404 and auth_client_secret is not None:
            _Warnings.auth_with_anon_weaviate()
            self._client = self.__make_client()
        else:
            self._client = self.__make_client()

    def _create_background_token_refresh(self, _auth: Optional[_Auth] = None) -> None:
        """Create a background thread that periodically refreshes access and refresh tokens.

        While the underlying library refreshes tokens, it does not have an internal cronjob that checks every
        X-seconds if a token has expired. If there is no activity for longer than the refresh tokens lifetime, it will
        expire. Therefore, refresh manually shortly before expiration time is up."""
        assert isinstance(self._client, OAuth2Client)
        if "refresh_token" not in self._client.token and _auth is None:
            return

        expires_in: int = self._client.token.get(
            "expires_in", 60
        )  # use 1minute as token lifetime if not supplied
        self._shutdown_background_event = Event()

        def periodic_refresh_token(refresh_time: int, _auth: Optional[_Auth]) -> None:
            time.sleep(max(refresh_time - 30, 1))
            while (
                self._shutdown_background_event is not None
                and not self._shutdown_background_event.is_set()
            ):
                # use refresh token when available
                try:
                    if "refresh_token" in cast(OAuth2Client, self._client).token:
                        assert isinstance(self._client, OAuth2Client)
                        self._client.token = self._client.refresh_token(
                            self._client.metadata["token_endpoint"]
                        )
                        refresh_time = self._client.token.get("expires_in") - 30
                    else:
                        # client credentials usually does not contain a refresh token => get a new token using the
                        # saved credentials
                        assert _auth is not None
                        new_session = _auth.get_sync_auth_client()
                        self._client.token = new_session.fetch_token()
                except (HTTPError, ReadTimeout) as exc:
                    # retry again after one second, might be an unstable connection
                    refresh_time = 1
                    _Warnings.token_refresh_failed(exc)

                time.sleep(max(refresh_time, 1))

        demon = Thread(
            target=periodic_refresh_token,
            args=(expires_in, _auth),
            daemon=True,
            name="TokenRefresh",
        )
        demon.start()

    async def close(self) -> None:
        """Shutdown connection class gracefully."""
        # in case an exception happens before definition of these members
        if hasattr(self, "_client"):
            await self._client.aclose()

    def _get_request_header(self) -> dict:
        """
        Returns the correct headers for a request.

        Returns
        -------
        dict
            Request header as a dict.
        """
        return self._headers

    def get_current_bearer_token(self) -> str:
        if "authorization" in self._headers:
            return self._headers["authorization"]
        elif isinstance(self._client, AsyncOAuth2Client):
            return f"Bearer {self._client.token['access_token']}"

        return ""

    def _get_additional_headers(self) -> Dict[str, str]:
        """Returns the additional headers."""
        return self.__additional_headers

    async def delete(
        self,
        path: str,
        weaviate_object: Optional[JSONPayload] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make a DELETE request to the Weaviate server instance.

        Parameters
        ----------
        path : str
            Sub-path to the Weaviate resources. Must be a valid Weaviate sub-path.
            e.g. '/meta' or '/objects', without version.
        weaviate_object : dict, optional
            Object is used as payload for DELETE request. By default None.
        params : dict, optional
            Additional request parameters, by default None

        Returns
        -------
        httpx.Response
            The response, if request was successful.

        Raises
        ------
        httpx.ConnectionError
            If the DELETE request could not be made.
        """
        if self.embedded_db is not None:
            self.embedded_db.ensure_running()
        request_url = self.url + self._api_version_path + path

        # Must build manually because httpx is opinionated about sending JSON in DELETE requests
        # From httpx docs:
        # Note that the data, files, json and content parameters are not available on this function, as DELETE requests should not include a request body.
        request = self._client.build_request(
            "DELETE",
            url=request_url,
            json=weaviate_object,
            params=params,
        )
        res = await self._client.send(request)
        return cast(Response, res)

    async def patch(
        self,
        path: str,
        weaviate_object: JSONPayload,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make a PATCH request to the Weaviate server instance.

        Parameters
        ----------
        path : str
            Sub-path to the Weaviate resources. Must be a valid Weaviate sub-path.
            e.g. '/meta' or '/objects', without version.
        weaviate_object : dict
            Object is used as payload for PATCH request.
        params : dict, optional
            Additional request parameters, by default None
        Returns
        -------
        httpx.Response
            The response, if request was successful.

        Raises
        ------
        httpx.ConnectionError
            If the PATCH request could not be made.
        """
        if self.embedded_db is not None:
            self.embedded_db.ensure_running()
        request_url = self.url + self._api_version_path + path

        res = await self._client.patch(
            url=request_url,
            json=weaviate_object,
            params=params,
        )
        return cast(Response, res)

    async def post(
        self,
        path: str,
        weaviate_object: JSONPayload,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make a POST request to the Weaviate server instance.

        Parameters
        ----------
        path : str
            Sub-path to the Weaviate resources. Must be a valid Weaviate sub-path.
            e.g. '/meta' or '/objects', without version.
        weaviate_object : dict
            Object is used as payload for POST request.
        params : dict, optional
            Additional request parameters, by default None
        external_url: Is an external (non-weaviate) url called

        Returns
        -------
        httpx.Response
            The response, if request was successful.

        Raises
        ------
        httpx.ConnectionError
            If the POST request could not be made.
        """
        if self.embedded_db is not None:
            self.embedded_db.ensure_running()
        request_url = self.url + self._api_version_path + path

        res = await self._client.post(
            url=request_url,
            json=weaviate_object,
            params=params,
        )
        return cast(Response, res)

    async def put(
        self,
        path: str,
        weaviate_object: JSONPayload,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make a PUT request to the Weaviate server instance.

        Parameters
        ----------
        path : str
            Sub-path to the Weaviate resources. Must be a valid Weaviate sub-path.
            e.g. '/meta' or '/objects', without version.
        weaviate_object : dict
            Object is used as payload for PUT request.
        params : dict, optional
            Additional request parameters, by default None
        Returns
        -------
        httpx.Response
            The response, if request was successful.

        Raises
        ------
        httpx.ConnectionError
            If the PUT request could not be made.
        """
        if self.embedded_db is not None:
            self.embedded_db.ensure_running()
        request_url = self.url + self._api_version_path + path

        res = await self._client.put(
            url=request_url,
            json=weaviate_object,
            params=params,
        )
        return cast(Response, res)

    async def get(
        self, path: str, params: Optional[Dict[str, Any]] = None, external_url: bool = False
    ) -> Response:
        """Make a GET request.

        Parameters
        ----------
        path : str
            Sub-path to the Weaviate resources. Must be a valid Weaviate sub-path.
            e.g. '/meta' or '/objects', without version.
        params : dict, optional
            Additional request parameters, by default None
        external_url: Is an external (non-weaviate) url called

        Returns
        -------
        httpx.Response
            The response if request was successful.

        Raises
        ------
        httpx.ConnectionError
            If the GET request could not be made.
        """
        if self.embedded_db is not None:
            self.embedded_db.ensure_running()
        if params is None:
            params = {}

        if external_url:
            request_url = path
        else:
            request_url = self.url + self._api_version_path + path

        res = await self._client.get(
            url=request_url,
            params=params,
        )
        return cast(Response, res)

    async def head(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make a HEAD request to the server.

        Parameters
        ----------
        path : str
            Sub-path to the resources. Must be a valid sub-path.
            e.g. '/meta' or '/objects', without version.
        params : dict, optional
            Additional request parameters, by default None

        Returns
        -------
        httpx.Response
            The response to the request.

        Raises
        ------
        httpx.ConnectionError
            If the HEAD request could not be made.
        """
        if self.embedded_db is not None:
            self.embedded_db.ensure_running()
        request_url = self.url + self._api_version_path + path

        res = await self._client.head(
            url=request_url,
            params=params,
        )
        return cast(Response, res)

    @property
    def proxies(self) -> dict:
        return self._proxies

    async def wait_for_weaviate(self, startup_period: int) -> None:
        """
        Waits until weaviate is ready or the timelimit given in 'startup_period' has passed.

        Parameters
        ----------
        startup_period : int
            Describes how long the client will wait for weaviate to start in seconds.

        Raises
        ------
        WeaviateStartUpError
            If weaviate takes longer than the timelimit to respond.
        """

        ready_url = self.url + self._api_version_path + "/.well-known/ready"
        async with AsyncClient() as client:
            for _i in range(startup_period):
                try:
                    res = await client.get(ready_url, headers=self._get_request_header())
                    res.raise_for_status()
                    return
                except (ConnectError, HTTPError):
                    time.sleep(1)

            try:
                res = await client.get(ready_url, headers=self._get_request_header())
                res.raise_for_status()
                return
            except (ConnectError, HTTPError) as error:
                raise WeaviateStartUpError(
                    f"Weaviate did not start up in {startup_period} seconds. Either the Weaviate URL {self.url} is wrong or Weaviate did not start up in the interval given in 'startup_period'."
                ) from error

    def grpc_stub(self) -> Optional[weaviate_pb2_grpc.WeaviateStub]:
        return self._grpc_stub

    def grpc_available(self) -> bool:
        return self._grpc_available

    def get_proxies(self) -> dict:
        return self._proxies

    @property
    def additional_headers(self) -> Dict[str, str]:
        return self.__additional_headers

    async def get_meta(self) -> Dict[str, str]:
        """
        Returns the meta endpoint.
        """
        response = await self.get(path="/meta")
        res = _decode_json_response_dict(response, "Meta endpoint")
        assert res is not None
        return res


def _get_proxies(proxies: Union[dict, str, None], trust_env: bool) -> dict:
    """
    Get proxies as dict, compatible with 'requests' library.
    NOTE: 'proxies' has priority over 'trust_env', i.e. if 'proxies' is NOT None, 'trust_env'
    is ignored.

    Parameters
    ----------
    proxies : dict, str or None
        The proxies to use for requests. If it is a dict it should follow 'requests' library
        format (https://docs.python-requests.org/en/stable/user/advanced/#proxies). If it is
        a URL (str), a dict will be constructed with both 'http' and 'https' pointing to that
        URL. If None, no proxies will be used.
    trust_env : bool
        If True, the proxies will be read from ENV VARs (case insensitive):
            HTTP_PROXY/HTTPS_PROXY.
        NOTE: It is ignored if 'proxies' is NOT None.

    Returns
    -------
    dict
        A dictionary with proxies, either set from 'proxies' or read from ENV VARs.
    """

    if proxies is not None:
        if isinstance(proxies, str):
            return {
                "http": proxies,
                "https": proxies,
            }
        if isinstance(proxies, dict):
            return proxies
        raise TypeError(
            "If 'proxies' is not None, it must be of type dict or str. "
            f"Given type: {type(proxies)}."
        )

    if not trust_env:
        return {}

    http_proxy = (os.environ.get("HTTP_PROXY"), os.environ.get("http_proxy"))
    https_proxy = (os.environ.get("HTTPS_PROXY"), os.environ.get("https_proxy"))

    if not any(http_proxy + https_proxy):
        return {}

    proxies = {}
    if any(http_proxy):
        proxies["http"] = http_proxy[0] if http_proxy[0] else http_proxy[1]
    if any(https_proxy):
        proxies["https"] = https_proxy[0] if https_proxy[0] else https_proxy[1]

    return proxies
