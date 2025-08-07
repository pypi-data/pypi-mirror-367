"""Base for API and client manager classes.
"""
import json
from typing import Any, Callable, Protocol, Awaitable, Mapping, Self

from ..exceptions import AuthError, APIError
from ..generated import AuthenticatedClient, Client

__all__ = (
    "AuthError", "APIError",
    "AuthenticatedClient", "Client",
    "BaseAPI",
    "BaseClientManager",
)


class SyncFunctionProtocol[T](Protocol):
    def __call__(self, realm: str, *, client: AuthenticatedClient | Client, **kwds) -> T:
        """Protocol for synchronous functions that take a realm and client.
        """
        ...


class SyncDetailedFunctionProtocol[T](Protocol):
    def __call__(self, realm: str, *, client: AuthenticatedClient | Client, body: Any | None = None, **kwds) -> T:
        """Protocol for synchronous functions that take a realm and client,
        returning a detailed response.
        """
        ...


class AsyncFunctionProtocol[T](Protocol):
    async def __call__(self, realm: str, *, client: AuthenticatedClient | Client, **kwds) -> T:
        """Protocol for asynchronous functions that take a realm and client.
        """
        ...


class AsyncDetailedFunctionProtocol[T](Protocol):
    async def __call__(self, realm: str, *, client: AuthenticatedClient | Client, body: Any | None = None, **kwds) -> T:
        """Protocol for asynchronous functions that take a realm and client,
        returning a detailed response.
        """
        ...

class AdditionalPropertiesContainerTypeProtocol[T](Protocol):
    """Protocol for types that can contain additional properties.

    This is used to ensure that the type has an `additional_properties` attribute.
    """
    additional_properties: dict[str, T] | None

    def to_dict(self) -> dict[str, T]:
        """Convert the instance to a dictionary."""
        ...

    @classmethod
    def from_dict(cls, data: Mapping[str, T]) -> Self:
        """Create an instance from a dictionary."""
        ...


class BaseAPI:
    """Base class that provides common functionality for API classes.
    """
    manager: "BaseClientManager"
    _realm: str | None

    def __init__(self, manager: "BaseClientManager", realm: str | None = None):
        self.manager = manager
        self._realm = realm

    @property
    def realm(self) -> str:
        return self._realm or self.manager.realm or "master"

    @property
    def _client(self) -> AuthenticatedClient:
        return self.manager.client

    def _sync_any[T](self, func: Callable[..., T], **kwds) -> T:
        return func(client=self._client, **kwds)

    async def _async_any[T](self, func: Callable[..., Awaitable[T]], **kwds) -> T:
        return await func(client=self._client, **kwds)

    def _sync[T](self, func: SyncFunctionProtocol[T] | Callable[..., T], realm: str | None, **kwds) -> T:
        return self._sync_any(func, realm=realm or self.realm, **kwds)

    def _sync_ap[T](self, func: SyncFunctionProtocol[AdditionalPropertiesContainerTypeProtocol[T]] | Callable[..., AdditionalPropertiesContainerTypeProtocol[T]], realm: str | None, **kwds) -> dict[str, T] | None:
        """Helper for endpoints that return additional properties."""
        result = self._sync_any(func, realm=realm or self.realm, **kwds)
        if result:
            return result.to_dict()
        return result

    def _sync_ap_list[T](self, func: SyncFunctionProtocol[list[AdditionalPropertiesContainerTypeProtocol[T]]] | Callable[..., list[AdditionalPropertiesContainerTypeProtocol[T]]], realm: str | None, **kwds) -> list[dict[str, T]] | None:
        """Helper for endpoints that return a list of additional properties."""
        result = self._sync_any(func, realm=realm or self.realm, **kwds)
        if result:
            return [item.to_dict() for item in result]
        return result

    def _sync_detailed[T](self, func: SyncDetailedFunctionProtocol[T] | Callable[..., T], realm: str | None, body: Any | None = None, **kwds) -> T:
        return self._sync_any(func, realm=realm or self.realm, body=body, **kwds)
    
    def _sync_detailed_json[T](self, func: SyncDetailedFunctionProtocol[T] | Callable[..., T], realm: str | None, body: dict | str, **kwds) -> T:
        """Helper for endpoints that expect JSON string body."""
        body_json = json.dumps(body) if isinstance(body, dict) else body
        return self._sync_any(func, realm=realm or self.realm, body=body_json, **kwds)
    
    def _sync_detailed_model[T, M](self, func: SyncDetailedFunctionProtocol[T] | Callable[..., T], realm: str | None, body: dict | M, model_class: type[M], **kwds) -> T:
        """Helper for endpoints that expect model objects, accepting either dict or model instance."""
        if isinstance(body, dict):
            body_obj = model_class.from_dict(body)
        else:
            body_obj = body
        return self._sync_any(func, realm=realm or self.realm, body=body_obj, **kwds)

    async def _async[T](self, func: AsyncFunctionProtocol[T] | Callable[..., Awaitable[T]], realm: str | None, **kwds) -> T:
        return await self._async_any(func, realm=realm or self.realm, **kwds)

    async def _async_ap[T](self, func: AsyncFunctionProtocol[AdditionalPropertiesContainerTypeProtocol[T]] | Callable[..., Awaitable[AdditionalPropertiesContainerTypeProtocol[T]]], realm: str | None, **kwds) -> dict[str, T] | None:
        """Helper for endpoints that return additional properties."""
        result = await self._async_any(func, realm=realm or self.realm, **kwds)
        if result:
            return result.to_dict()
        return result

    async def _async_ap_list[T](self, func: AsyncFunctionProtocol[list[AdditionalPropertiesContainerTypeProtocol[T]]] | Callable[..., Awaitable[list[AdditionalPropertiesContainerTypeProtocol[T]]]], realm: str | None, **kwds) -> list[dict[str, T]] | None:
        """Helper for endpoints that return a list of additional properties."""
        result = await self._async_any(func, realm=realm or self.realm, **kwds)
        if result:
            return [item.to_dict() for item in result]
        return result

    async def _async_detailed[T](self, func: AsyncDetailedFunctionProtocol[T] | Callable[..., Awaitable[T]], realm: str | None, body: Any | None = None, **kwds) -> T:
        return await self._async_any(func, realm=realm or self.realm, body=body, **kwds)
    
    async def _async_detailed_json[T](self, func: AsyncDetailedFunctionProtocol[T] | Callable[..., Awaitable[T]], realm: str | None, body: dict | str, **kwds) -> T:
        """Helper for endpoints that expect JSON string body."""
        body_json = json.dumps(body) if isinstance(body, dict) else body
        return await self._async_any(func, realm=realm or self.realm, body=body_json, **kwds)
    
    async def _async_detailed_model[T, M](self, func: AsyncDetailedFunctionProtocol[T] | Callable[..., Awaitable[T]], realm: str | None, body: dict | M, model_class: type[M], **kwds) -> T:
        """Helper for endpoints that expect model objects, accepting either dict or model instance."""
        if isinstance(body, dict):
            body_obj = model_class.from_dict(body)
        else:
            body_obj = body
        return await self._async_any(func, realm=realm or self.realm, body=body_obj, **kwds)


class BaseClientManager:
    """Mixin to manage the authenticated client.
    """
    _client: AuthenticatedClient | None = None
    _in_async_context: bool = False
    realm: str = "master"

    def __init__(self, realm: str | None = None):
        if realm:
            self.realm = realm

    @property
    def client(self) -> AuthenticatedClient:
        """The authenticated client (triggers authentication if not set).
        """
        if self._client is None:
            if self._in_async_context:
                raise AuthError("Cannot access client in async context without authentication. Use `async with` to ensure authentication.")

            self._ensure_authenticated()

        if self._client is None:
            raise AuthError("Client is not authenticated.")

        return self._client

    def _ensure_authenticated(self):
        raise NotImplementedError("Subclasses must implement _ensure_authenticated()")

    async def _ensure_authenticated_async(self):
        raise NotImplementedError("Subclasses must implement _ensure_authenticated_async()")

    def __enter__(self):
        """Enter sync context."""
        self._in_async_context = False

        self._ensure_authenticated()
        self._client.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sync context."""
        self._in_async_context = False

        if self._client:
            self._client.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        """Enter async context."""
        self._in_async_context = True

        await self._ensure_authenticated_async()
        await self._client.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        self._in_async_context = False

        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
