"""Client scope management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.client_scopes import (
    get_admin_realms_realm_client_scopes,
    post_admin_realms_realm_client_scopes,
    get_admin_realms_realm_client_scopes_client_scope_id,
    put_admin_realms_realm_client_scopes_client_scope_id,
    delete_admin_realms_realm_client_scopes_client_scope_id,
)
from ..generated.models import ClientScopeRepresentation

__all__ = "ClientScopesAPI", "ClientScopesClientMixin", "ClientScopeRepresentation"


class ClientScopesAPI(BaseAPI):
    """Client scope management API methods."""

    def get_all(self, realm: str | None = None) -> list[ClientScopeRepresentation] | None:
        """List client scopes in a realm (sync).
        
        Client scopes define sets of protocol mappers and roles that can be shared between clients.
        
        Args:
            realm: The realm name
            
        Returns:
            List of client scopes configured in the realm
        """
        return self._sync(get_admin_realms_realm_client_scopes.sync, realm)

    async def aget_all(self, realm: str | None = None) -> list[ClientScopeRepresentation] | None:
        """List client scopes in a realm (async).
        
        Client scopes define sets of protocol mappers and roles that can be shared between clients.
        
        Args:
            realm: The realm name
            
        Returns:
            List of client scopes configured in the realm
        """
        return await self._async(get_admin_realms_realm_client_scopes.asyncio, realm)

    def create(self, realm: str | None = None, *, scope_data: dict | ClientScopeRepresentation) -> str:
        """Create a client scope (sync).
        
        Args:
            realm: The realm name
            scope_data: Client scope configuration including name, protocol, and attributes
            
        Returns:
            Created client scope ID
            
        Raises:
            APIError: If client scope creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_client_scopes.sync_detailed,
            realm,
            scope_data,
            ClientScopeRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client scope: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def acreate(self, realm: str | None = None, *, scope_data: dict | ClientScopeRepresentation) -> str:
        """Create a client scope (async).
        
        Args:
            realm: The realm name
            scope_data: Client scope configuration including name, protocol, and attributes
            
        Returns:
            Created client scope ID
            
        Raises:
            APIError: If client scope creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_client_scopes.asyncio_detailed,
            realm,
            scope_data,
            ClientScopeRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client scope: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def get(self, realm: str | None = None, *, client_scope_id: str) -> ClientScopeRepresentation | None:
        """Get a client scope by ID (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            
        Returns:
            Client scope representation with full details
        """
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id.sync,
            realm,
            client_scope_id=client_scope_id
        )

    async def aget(self, realm: str | None = None, *, client_scope_id: str) -> ClientScopeRepresentation | None:
        """Get a client scope by ID (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            
        Returns:
            Client scope representation with full details
        """
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id.asyncio,
            realm,
            client_scope_id=client_scope_id
        )

    def update(self, realm: str | None = None, *, client_scope_id: str,
               scope_data: dict | ClientScopeRepresentation) -> None:
        """Update a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to update
            scope_data: Updated client scope configuration
            
        Raises:
            APIError: If client scope update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_client_scopes_client_scope_id.sync_detailed,
            realm,
            scope_data,
            ClientScopeRepresentation,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client scope: {response.status_code}")

    async def aupdate(self, realm: str | None = None, *, client_scope_id: str,
                      scope_data: dict | ClientScopeRepresentation) -> None:
        """Update a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to update
            scope_data: Updated client scope configuration
            
        Raises:
            APIError: If client scope update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            scope_data,
            ClientScopeRepresentation,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client scope: {response.status_code}")

    def delete(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Delete a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to delete
            
        Raises:
            APIError: If client scope deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client scope: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Delete a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to delete
            
        Raises:
            APIError: If client scope deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client scope: {response.status_code}")


class ClientScopesClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ClientScopesAPI.
    """

    @cached_property
    def client_scopes(self) -> ClientScopesAPI:
        """Get the ClientScopesAPI instance."""
        return ClientScopesAPI(manager=self)  # type: ignore[arg-type]
