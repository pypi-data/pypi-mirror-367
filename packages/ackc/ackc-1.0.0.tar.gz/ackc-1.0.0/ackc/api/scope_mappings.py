"""Scope mappings API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.scope_mappings import (
    # Client scope mappings
    get_admin_realms_realm_clients_client_uuid_scope_mappings,
    get_admin_realms_realm_clients_client_uuid_scope_mappings_realm,
    get_admin_realms_realm_clients_client_uuid_scope_mappings_realm_available,
    get_admin_realms_realm_clients_client_uuid_scope_mappings_realm_composite,
    post_admin_realms_realm_clients_client_uuid_scope_mappings_realm,
    delete_admin_realms_realm_clients_client_uuid_scope_mappings_realm,
    get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client,
    get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client_available,
    get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client_composite,
    post_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client,
    delete_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client,
    # Client scope scope mappings
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings,
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm,
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm_available,
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm_composite,
    post_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm,
    delete_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm,
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client,
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client_available,
    get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client_composite,
    post_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client,
    delete_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client,
)
from ..generated.models import MappingsRepresentation, RoleRepresentation
from ..generated.types import UNSET, Unset

__all__ = "ScopeMappingsAPI", "ScopeMappingsClientMixin"


class ScopeMappingsAPI(BaseAPI):
    """Scope mappings API methods."""

    # Client scope mappings
    def get_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str) -> MappingsRepresentation | None:
        """Get all scope mappings for a client.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Complete scope mappings including realm and client scopes
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str) -> MappingsRepresentation | None:
        """Get all scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_client_realm_scope_mappings(self, realm: str | None = None, *, client_uuid: str) -> list[RoleRepresentation] | None:
        """Get realm-level scope mappings for a client.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of realm roles in the client's scope
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_realm.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_realm_scope_mappings(self, realm: str | None = None, *, client_uuid: str) -> list[RoleRepresentation] | None:
        """Get realm-level scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_realm.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_client_realm_scope_mappings_available(self, realm: str | None = None, *, client_uuid: str) -> list[RoleRepresentation] | None:
        """Get available realm-level scope mappings for a client.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of realm roles that can be added to the client's scope
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_realm_available.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_realm_scope_mappings_available(self, realm: str | None = None, *, client_uuid: str) -> list[RoleRepresentation] | None:
        """Get available realm-level scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_realm_available.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_client_realm_scope_mappings_composite(self, realm: str | None = None, *, client_uuid: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level scope mappings for a client.
        
        Includes roles in scope directly and through composite roles.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective realm roles in the client's scope
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_realm_composite.sync,
            realm,
            client_uuid=client_uuid,
            brief_representation=brief_representation
        )

    async def aget_client_realm_scope_mappings_composite(self, realm: str | None = None, *, client_uuid: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_realm_composite.asyncio,
            realm,
            client_uuid=client_uuid,
            brief_representation=brief_representation
        )

    def add_client_realm_scope_mappings(self, realm: str | None = None, *, client_uuid: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level scope mappings to a client.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            roles: List of realm roles to add to the client's scope
            
        Raises:
            APIError: If adding scope mappings fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_clients_client_uuid_scope_mappings_realm.sync_detailed,
            realm,
            client_uuid=client_uuid,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm scope mappings: {response.status_code}")

    async def aadd_client_realm_scope_mappings(self, realm: str | None = None, *, client_uuid: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level scope mappings to a client (async)."""
        response = await self._async_detailed(
            post_admin_realms_realm_clients_client_uuid_scope_mappings_realm.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm scope mappings: {response.status_code}")

    def remove_client_realm_scope_mappings(self, realm: str | None = None, *, client_uuid: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level scope mappings from a client.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            roles: List of realm roles to remove from the client's scope
            
        Raises:
            APIError: If removing scope mappings fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_clients_client_uuid_scope_mappings_realm.sync_detailed,
            realm,
            client_uuid=client_uuid,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm scope mappings: {response.status_code}")

    async def aremove_client_realm_scope_mappings(self, realm: str | None = None, *, client_uuid: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level scope mappings from a client (async)."""
        response = await self._async_detailed(
            delete_admin_realms_realm_clients_client_uuid_scope_mappings_realm.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm scope mappings: {response.status_code}")

    def get_client_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str, client: str) -> list[RoleRepresentation] | None:
        """Get client-level scope mappings for a client."""
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client.sync,
            realm,
            client_uuid=client_uuid,
            client_path=client
        )

    async def aget_client_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str, client: str) -> list[RoleRepresentation] | None:
        """Get client-level scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client.asyncio,
            realm,
            client_uuid=client_uuid,
            client_path=client
        )

    def get_client_client_scope_mappings_available(self, realm: str | None = None, *, client_uuid: str, client: str) -> list[RoleRepresentation] | None:
        """Get available client-level scope mappings for a client."""
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client_available.sync,
            realm,
            client_uuid=client_uuid,
            client_path=client
        )

    async def aget_client_client_scope_mappings_available(self, realm: str | None = None, *, client_uuid: str, client: str) -> list[RoleRepresentation] | None:
        """Get available client-level scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client_available.asyncio,
            realm,
            client_uuid=client_uuid,
            client_path=client
        )

    def get_client_client_scope_mappings_composite(self, realm: str | None = None, *, client_uuid: str, client: str) -> list[RoleRepresentation] | None:
        """Get composite client-level scope mappings for a client."""
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client_composite.sync,
            realm,
            client_uuid=client_uuid,
            client_path=client
        )

    async def aget_client_client_scope_mappings_composite(self, realm: str | None = None, *, client_uuid: str, client: str) -> list[RoleRepresentation] | None:
        """Get composite client-level scope mappings for a client (async)."""
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client_composite.asyncio,
            realm,
            client_uuid=client_uuid,
            client_path=client
        )

    def add_client_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level scope mappings to a client."""
        response = self._sync_detailed(
            post_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client.sync_detailed,
            realm,
            client_uuid=client_uuid,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client scope mappings: {response.status_code}")

    async def aadd_client_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level scope mappings to a client (async)."""
        response = await self._async_detailed(
            post_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client scope mappings: {response.status_code}")

    def remove_client_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level scope mappings from a client."""
        response = self._sync_detailed(
            delete_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client.sync_detailed,
            realm,
            client_uuid=client_uuid,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client scope mappings: {response.status_code}")

    async def aremove_client_client_scope_mappings(self, realm: str | None = None, *, client_uuid: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level scope mappings from a client (async)."""
        response = await self._async_detailed(
            delete_admin_realms_realm_clients_client_uuid_scope_mappings_clients_client.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client scope mappings: {response.status_code}")

    # Client scope scope mappings
    def get_client_scope_scope_mappings(self, realm: str | None = None, *, client_scope_id: str) -> MappingsRepresentation | None:
        """Get all scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings.sync,
            realm,
            client_scope_id=client_scope_id
        )

    async def aget_client_scope_scope_mappings(self, realm: str | None = None, *, client_scope_id: str) -> MappingsRepresentation | None:
        """Get all scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings.asyncio,
            realm,
            client_scope_id=client_scope_id
        )

    def get_client_scope_realm_scope_mappings(self, realm: str | None = None, *, client_scope_id: str) -> list[RoleRepresentation] | None:
        """Get realm-level scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm.sync,
            realm,
            client_scope_id=client_scope_id
        )

    async def aget_client_scope_realm_scope_mappings(self, realm: str | None = None, *, client_scope_id: str) -> list[RoleRepresentation] | None:
        """Get realm-level scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm.asyncio,
            realm,
            client_scope_id=client_scope_id
        )

    def get_client_scope_realm_scope_mappings_available(self, realm: str | None = None, *, client_scope_id: str) -> list[RoleRepresentation] | None:
        """Get available realm-level scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm_available.sync,
            realm,
            client_scope_id=client_scope_id
        )

    async def aget_client_scope_realm_scope_mappings_available(self, realm: str | None = None, *, client_scope_id: str) -> list[RoleRepresentation] | None:
        """Get available realm-level scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm_available.asyncio,
            realm,
            client_scope_id=client_scope_id
        )

    def get_client_scope_realm_scope_mappings_composite(self, realm: str | None = None, *, client_scope_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm_composite.sync,
            realm,
            client_scope_id=client_scope_id,
            brief_representation=brief_representation
        )

    async def aget_client_scope_realm_scope_mappings_composite(self, realm: str | None = None, *, client_scope_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm_composite.asyncio,
            realm,
            client_scope_id=client_scope_id,
            brief_representation=brief_representation
        )

    def add_client_scope_realm_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level scope mappings to a client scope."""
        response = self._sync_detailed(
            post_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm scope mappings: {response.status_code}")

    async def aadd_client_scope_realm_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level scope mappings to a client scope (async)."""
        response = await self._async_detailed(
            post_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm scope mappings: {response.status_code}")

    def remove_client_scope_realm_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level scope mappings from a client scope."""
        response = self._sync_detailed(
            delete_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm scope mappings: {response.status_code}")

    async def aremove_client_scope_realm_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level scope mappings from a client scope (async)."""
        response = await self._async_detailed(
            delete_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_realm.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm scope mappings: {response.status_code}")

    def get_client_scope_client_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, client: str) -> list[RoleRepresentation] | None:
        """Get client-level scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client.sync,
            realm,
            client_scope_id=client_scope_id,
            client_path=client
        )

    async def aget_client_scope_client_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, client: str) -> list[RoleRepresentation] | None:
        """Get client-level scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client.asyncio,
            realm,
            client_scope_id=client_scope_id,
            client_path=client
        )

    def get_client_scope_client_scope_mappings_available(self, realm: str | None = None, *, client_scope_id: str, client: str) -> list[RoleRepresentation] | None:
        """Get available client-level scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client_available.sync,
            realm,
            client_scope_id=client_scope_id,
            client_path=client
        )

    async def aget_client_scope_client_scope_mappings_available(self, realm: str | None = None, *, client_scope_id: str, client: str) -> list[RoleRepresentation] | None:
        """Get available client-level scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client_available.asyncio,
            realm,
            client_scope_id=client_scope_id,
            client_path=client
        )

    def get_client_scope_client_scope_mappings_composite(self, realm: str | None = None, *, client_scope_id: str, client: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite client-level scope mappings for a client scope."""
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client_composite.sync,
            realm,
            client_scope_id=client_scope_id,
            client_path=client,
            brief_representation=brief_representation
        )

    async def aget_client_scope_client_scope_mappings_composite(self, realm: str | None = None, *, client_scope_id: str, client: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite client-level scope mappings for a client scope (async)."""
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client_composite.asyncio,
            realm,
            client_scope_id=client_scope_id,
            client_path=client,
            brief_representation=brief_representation
        )

    def add_client_scope_client_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level scope mappings to a client scope."""
        response = self._sync_detailed(
            post_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client scope mappings: {response.status_code}")

    async def aadd_client_scope_client_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level scope mappings to a client scope (async)."""
        response = await self._async_detailed(
            post_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client scope mappings: {response.status_code}")

    def remove_client_scope_client_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level scope mappings from a client scope."""
        response = self._sync_detailed(
            delete_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client scope mappings: {response.status_code}")

    async def aremove_client_scope_client_scope_mappings(self, realm: str | None = None, *, client_scope_id: str, client: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level scope mappings from a client scope (async)."""
        response = await self._async_detailed(
            delete_admin_realms_realm_client_scopes_client_scope_id_scope_mappings_clients_client.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
            client_path=client,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client scope mappings: {response.status_code}")


class ScopeMappingsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ScopeMappingsAPI."""
    
    @cached_property
    def scope_mappings(self) -> ScopeMappingsAPI:
        """Get the ScopeMappingsAPI instance."""
        return ScopeMappingsAPI(manager=self)  # type: ignore[arg-type]