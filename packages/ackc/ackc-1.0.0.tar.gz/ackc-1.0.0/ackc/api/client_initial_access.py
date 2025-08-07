"""Client initial access API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.client_initial_access import (
    get_admin_realms_realm_clients_initial_access,
    post_admin_realms_realm_clients_initial_access,
    delete_admin_realms_realm_clients_initial_access_id,
)
from ..generated.models import ClientInitialAccessPresentation, ClientInitialAccessCreatePresentation

__all__ = (
    "ClientInitialAccessAPI",
    "ClientInitialAccessClientMixin",
    "ClientInitialAccessPresentation",
    "ClientInitialAccessCreatePresentation",
)


class ClientInitialAccessAPI(BaseAPI):
    """Client initial access API methods."""

    def get_all(self, realm: str | None = None) -> list[ClientInitialAccessPresentation] | None:
        """Get all client initial access tokens.
        
        Args:
            realm: The realm name
            
        Returns:
            List of initial access tokens for dynamic client registration
        """
        return self._sync(
            get_admin_realms_realm_clients_initial_access.sync,
            realm
        )

    async def aget_all(self, realm: str | None = None) -> list[ClientInitialAccessPresentation] | None:
        """Get all client initial access tokens (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of initial access tokens for dynamic client registration
        """
        return await self._async(
            get_admin_realms_realm_clients_initial_access.asyncio,
            realm
        )

    def create(self, realm: str | None = None, *, config: dict | ClientInitialAccessCreatePresentation) -> ClientInitialAccessPresentation | None:
        """Create a new client initial access token.
        
        Creates a token that can be used for dynamic client registration.
        
        Args:
            realm: The realm name
            config: Token configuration including expiration and count
            
        Returns:
            Created initial access token with the token value
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_initial_access.sync_detailed,
            realm,
            config,
            ClientInitialAccessCreatePresentation
        )
        return response.parsed

    async def acreate(self, realm: str | None = None, *, config: dict | ClientInitialAccessCreatePresentation) -> ClientInitialAccessPresentation | None:
        """Create a new client initial access token (async).
        
        Creates a token that can be used for dynamic client registration.
        
        Args:
            realm: The realm name
            config: Token configuration including expiration and count
            
        Returns:
            Created initial access token with the token value
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_initial_access.asyncio_detailed,
            realm,
            config,
            ClientInitialAccessCreatePresentation
        )
        return response.parsed

    def delete(self, realm: str | None = None, *, id: str) -> None:
        """Delete a client initial access token.
        
        Args:
            realm: The realm name
            id: Token ID to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_initial_access_id.sync_detailed,
            realm,
            id=id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client initial access token: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, id: str) -> None:
        """Delete a client initial access token (async).
        
        Args:
            realm: The realm name
            id: Token ID to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_initial_access_id.asyncio_detailed,
            realm,
            id=id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client initial access token: {response.status_code}")


class ClientInitialAccessClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ClientInitialAccessAPI."""
    
    @cached_property
    def client_initial_access(self) -> ClientInitialAccessAPI:
        """Get the ClientInitialAccessAPI instance."""
        return ClientInitialAccessAPI(manager=self)  # type: ignore[arg-type]