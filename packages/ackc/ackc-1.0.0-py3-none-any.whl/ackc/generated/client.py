import ssl
from typing import Any

from attrs import define, field, evolve
import niquests





@define
class Client:
    """A class for keeping track of data related to the API

    The following are accepted as keyword arguments and will be used to construct niquests Sessions internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        niquests.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``niquests_args``: A dictionary of additional arguments to be passed to the ``niquests.Session`` and ``niquests.AsyncSession`` constructor.

        ``multiplexed``: Enable HTTP/2 multiplexing for better performance (default: True)

        ``pool_connections``: Number of connection pools to cache (default: 20)

        ``pool_maxsize``: Maximum number of connections to save in the pool (default: 100)


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
    """
    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str = field(alias="base_url")
    _cookies: dict[str, str] = field(factory=dict, kw_only=True, alias="cookies")
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: float | None = field(default=None, kw_only=True, alias="timeout")
    _verify_ssl: str | bool | ssl.SSLContext = field(default=True, kw_only=True, alias="verify_ssl")
    _follow_redirects: bool = field(default=False, kw_only=True, alias="follow_redirects")
    _multiplexed: bool = field(default=True, kw_only=True, alias="multiplexed")
    _pool_connections: int = field(default=20, kw_only=True, alias="pool_connections")
    _pool_maxsize: int = field(default=100, kw_only=True, alias="pool_maxsize")
    _niquests_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="niquests_args")
    _client: niquests.Session | None = field(default=None, init=False)
    _async_client: niquests.AsyncSession | None = field(default=None, init=False)

    def with_headers(self, headers: dict[str, str]) -> "Client":
        """Get a new client matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        if self._async_client is not None:
            self._async_client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: dict[str, str]) -> "Client":
        """Get a new client matching this one with additional cookies"""
        if self._client is not None:
            self._client.cookies.update(cookies)
        if self._async_client is not None:
            self._async_client.cookies.update(cookies)
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: float) -> "Client":
        """Get a new client matching this one with a new timeout (in seconds)"""
        if self._client is not None:
            self._client.timeout = timeout
        if self._async_client is not None:
            self._async_client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_niquests_client(self, client: niquests.Session) -> "Client":
        """Manually set the underlying niquests.Session

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def get_niquests_client(self) -> niquests.Session:
        """Get the underlying niquests.Session, constructing a new one if not previously set"""
        if self._client is None:
            self._client = niquests.Session(
                multiplexed=self._multiplexed,
                pool_connections=self._pool_connections,
                pool_maxsize=self._pool_maxsize,
                **self._niquests_args,
            )
            # Set base properties
            self._client.headers.update(self._headers)
            self._client.cookies.update(self._cookies)
            self._client.verify = self._verify_ssl
            self._client.timeout = self._timeout
            # niquests handles redirects differently
            self._client.max_redirects = 30 if self._follow_redirects else 0
        return self._client

    def __enter__(self) -> "Client":
        """Enter a context manager for self.client"""
        self.get_niquests_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwds: Any) -> None:
        """Exit a context manager for internal niquests.Session"""
        self.get_niquests_client().__exit__(*args, **kwds)

    def set_async_niquests_client(self, async_client: niquests.AsyncSession) -> "Client":
        """Manually set the underlying niquests.AsyncSession

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_async_niquests_client(self) -> niquests.AsyncSession:
        """Get the underlying niquests.AsyncSession, constructing a new one if not previously set"""
        if self._async_client is None:
            self._async_client = niquests.AsyncSession(
                multiplexed=self._multiplexed,
                pool_connections=self._pool_connections,
                pool_maxsize=self._pool_maxsize,
                **self._niquests_args,
            )
            # Set base properties
            self._async_client.headers.update(self._headers)
            self._async_client.cookies.update(self._cookies)
            self._async_client.verify = self._verify_ssl
            self._async_client.timeout = self._timeout
            # niquests handles redirects differently
            self._async_client.max_redirects = 30 if self._follow_redirects else 0
        return self._async_client

    async def __aenter__(self) -> "Client":
        """Enter a context manager for underlying niquests.AsyncSession"""
        await self.get_async_niquests_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwds: Any) -> None:
        """Exit a context manager for underlying niquests.AsyncSession"""
        await self.get_async_niquests_client().__aexit__(*args, **kwds)

    # Compatibility methods for code expecting httpx interface
    def get_httpx_client(self) -> niquests.Session:
        """Compatibility method - returns niquests Session"""
        return self.get_niquests_client()
    
    def get_async_httpx_client(self) -> niquests.AsyncSession:
        """Compatibility method - returns niquests AsyncSession"""
        return self.get_async_niquests_client()


@define
class AuthenticatedClient:
    """A Client which has been authenticated for use on secured endpoints

    The following are accepted as keyword arguments and will be used to construct niquests Sessions internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        niquests.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``niquests_args``: A dictionary of additional arguments to be passed to the ``niquests.Session`` and ``niquests.AsyncSession`` constructor.

        ``multiplexed``: Enable HTTP/2 multiplexing for better performance (default: True)

        ``pool_connections``: Number of connection pools to cache (default: 20)

        ``pool_maxsize``: Maximum number of connections to save in the pool (default: 100)


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
        token: The token to use for authentication
        prefix: The prefix to use for the Authorization header
        auth_header_name: The name of the Authorization header
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str = field(alias="base_url")
    _cookies: dict[str, str] = field(factory=dict, kw_only=True, alias="cookies")
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: float | None = field(default=None, kw_only=True, alias="timeout")
    _verify_ssl: str | bool | ssl.SSLContext = field(default=True, kw_only=True, alias="verify_ssl")
    _follow_redirects: bool = field(default=False, kw_only=True, alias="follow_redirects")
    _multiplexed: bool = field(default=True, kw_only=True, alias="multiplexed")
    _pool_connections: int = field(default=20, kw_only=True, alias="pool_connections")
    _pool_maxsize: int = field(default=100, kw_only=True, alias="pool_maxsize")
    _niquests_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="niquests_args")
    _client: niquests.Session | None = field(default=None, init=False)
    _async_client: niquests.AsyncSession | None = field(default=None, init=False)

    token: str
    prefix: str = "Bearer"
    auth_header_name: str = "Authorization"

    def with_headers(self, headers: dict[str, str]) -> "AuthenticatedClient":
        """Get a new client matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        if self._async_client is not None:
            self._async_client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: dict[str, str]) -> "AuthenticatedClient":
        """Get a new client matching this one with additional cookies"""
        if self._client is not None:
            self._client.cookies.update(cookies)
        if self._async_client is not None:
            self._async_client.cookies.update(cookies)
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: float) -> "AuthenticatedClient":
        """Get a new client matching this one with a new timeout (in seconds)"""
        if self._client is not None:
            self._client.timeout = timeout
        if self._async_client is not None:
            self._async_client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_niquests_client(self, client: niquests.Session) -> "AuthenticatedClient":
        """Manually set the underlying niquests.Session

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def get_niquests_client(self) -> niquests.Session:
        """Get the underlying niquests.Session, constructing a new one if not previously set"""
        if self._client is None:
            self._headers[self.auth_header_name] = f"{self.prefix} {self.token}" if self.prefix else self.token
            self._client = niquests.Session(
                multiplexed=self._multiplexed,
                pool_connections=self._pool_connections,
                pool_maxsize=self._pool_maxsize,
                **self._niquests_args,
            )
            # Set base properties
            self._client.headers.update(self._headers)
            self._client.cookies.update(self._cookies)
            self._client.verify = self._verify_ssl
            self._client.timeout = self._timeout
            # niquests handles redirects differently
            self._client.max_redirects = 30 if self._follow_redirects else 0
        return self._client

    def __enter__(self) -> "AuthenticatedClient":
        """Enter a context manager for self.client"""
        self.get_niquests_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwds: Any) -> None:
        """Exit a context manager for internal niquests.Session"""
        self.get_niquests_client().__exit__(*args, **kwds)

    def set_async_niquests_client(self, async_client: niquests.AsyncSession) -> "AuthenticatedClient":
        """Manually set the underlying niquests.AsyncSession

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_async_niquests_client(self) -> niquests.AsyncSession:
        """Get the underlying niquests.AsyncSession, constructing a new one if not previously set"""
        if self._async_client is None:
            self._headers[self.auth_header_name] = f"{self.prefix} {self.token}" if self.prefix else self.token
            self._async_client = niquests.AsyncSession(
                multiplexed=self._multiplexed,
                pool_connections=self._pool_connections,
                pool_maxsize=self._pool_maxsize,
                **self._niquests_args,
            )
            # Set base properties
            self._async_client.headers.update(self._headers)
            self._async_client.cookies.update(self._cookies)
            self._async_client.verify = self._verify_ssl
            self._async_client.timeout = self._timeout
            # niquests handles redirects differently
            self._async_client.max_redirects = 30 if self._follow_redirects else 0
        return self._async_client

    async def __aenter__(self) -> "AuthenticatedClient":
        """Enter a context manager for underlying niquests.AsyncSession"""
        await self.get_async_niquests_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwds: Any) -> None:
        """Exit a context manager for underlying niquests.AsyncSession"""
        await self.get_async_niquests_client().__aexit__(*args, **kwds)

    # Compatibility methods for code expecting httpx interface
    def get_httpx_client(self) -> niquests.Session:
        """Compatibility method - returns niquests Session"""
        return self.get_niquests_client()
    
    def get_async_httpx_client(self) -> niquests.AsyncSession:
        """Compatibility method - returns niquests AsyncSession"""
        return self.get_async_niquests_client()
