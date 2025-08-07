"""Client role mappings API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.client_role_mappings import (
    get_admin_realms_realm_users_user_id_role_mappings_clients_client_id,
    get_admin_realms_realm_users_user_id_role_mappings_clients_client_id_available,
    get_admin_realms_realm_users_user_id_role_mappings_clients_client_id_composite,
    post_admin_realms_realm_users_user_id_role_mappings_clients_client_id,
    delete_admin_realms_realm_users_user_id_role_mappings_clients_client_id,
    get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id,
    get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id_available,
    get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id_composite,
    post_admin_realms_realm_groups_group_id_role_mappings_clients_client_id,
    delete_admin_realms_realm_groups_group_id_role_mappings_clients_client_id,
)
from ..generated.models import RoleRepresentation
from ..generated.types import UNSET, Unset

__all__ = "ClientRoleMappingsAPI", "ClientRoleMappingsClientMixin"


class ClientRoleMappingsAPI(BaseAPI):
    """Client role mappings API methods."""

    def get_user_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get client-level role mappings for a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            
        Returns:
            List of roles mapped to the user for this client
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings_clients_client_id.sync,
            realm,
            user_id=user_id,
            client_id=client_id
        )

    async def aget_user_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get client-level role mappings for a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            
        Returns:
            List of roles mapped to the user for this client
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings_clients_client_id.asyncio,
            realm,
            user_id=user_id,
            client_id=client_id
        )

    def get_user_available_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get available client-level role mappings for a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            
        Returns:
            List of client roles that can be mapped to the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings_clients_client_id_available.sync,
            realm,
            user_id=user_id,
            client_id=client_id
        )

    async def aget_user_available_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get available client-level role mappings for a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            
        Returns:
            List of client roles that can be mapped to the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings_clients_client_id_available.asyncio,
            realm,
            user_id=user_id,
            client_id=client_id
        )

    def get_user_composite_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite client-level role mappings for a user.
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective client roles for the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings_clients_client_id_composite.sync,
            realm,
            user_id=user_id,
            client_id=client_id,
            brief_representation=brief_representation
        )

    async def aget_user_composite_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite client-level role mappings for a user (async).
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective client roles for the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings_clients_client_id_composite.asyncio,
            realm,
            user_id=user_id,
            client_id=client_id,
            brief_representation=brief_representation
        )

    def add_user_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level role mappings to a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            roles: List of roles to map to the user
            
        Raises:
            APIError: If the mapping fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_users_user_id_role_mappings_clients_client_id.sync_detailed,
            realm,
            user_id=user_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client role mappings: {response.status_code}")

    async def aadd_user_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level role mappings to a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            roles: List of roles to map to the user
            
        Raises:
            APIError: If the mapping fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_users_user_id_role_mappings_clients_client_id.asyncio_detailed,
            realm,
            user_id=user_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client role mappings: {response.status_code}")

    def remove_user_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level role mappings from a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            roles: List of roles to unmap from the user
            
        Raises:
            APIError: If the unmapping fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_users_user_id_role_mappings_clients_client_id.sync_detailed,
            realm,
            user_id=user_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client role mappings: {response.status_code}")

    async def aremove_user_client_role_mappings(self, realm: str | None = None, *, user_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level role mappings from a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_id: Client ID
            roles: List of roles to unmap from the user
            
        Raises:
            APIError: If the unmapping fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_users_user_id_role_mappings_clients_client_id.asyncio_detailed,
            realm,
            user_id=user_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client role mappings: {response.status_code}")

    def get_group_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get client-level role mappings for a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            
        Returns:
            List of roles mapped to the group for this client
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id.sync,
            realm,
            group_id=group_id,
            client_id=client_id
        )

    async def aget_group_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get client-level role mappings for a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            
        Returns:
            List of roles mapped to the group for this client
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id.asyncio,
            realm,
            group_id=group_id,
            client_id=client_id
        )

    def get_group_available_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get available client-level role mappings for a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            
        Returns:
            List of client roles that can be mapped to the group
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id_available.sync,
            realm,
            group_id=group_id,
            client_id=client_id
        )

    async def aget_group_available_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str) -> list[RoleRepresentation] | None:
        """Get available client-level role mappings for a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            
        Returns:
            List of client roles that can be mapped to the group
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id_available.asyncio,
            realm,
            group_id=group_id,
            client_id=client_id
        )

    def get_group_composite_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite client-level role mappings for a group.
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective client roles for the group
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id_composite.sync,
            realm,
            group_id=group_id,
            client_id=client_id,
            brief_representation=brief_representation
        )

    async def aget_group_composite_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite client-level role mappings for a group (async).
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective client roles for the group
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings_clients_client_id_composite.asyncio,
            realm,
            group_id=group_id,
            client_id=client_id,
            brief_representation=brief_representation
        )

    def add_group_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level role mappings to a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            roles: List of roles to map to the group
            
        Raises:
            APIError: If the mapping fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_groups_group_id_role_mappings_clients_client_id.sync_detailed,
            realm,
            group_id=group_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client role mappings: {response.status_code}")

    async def aadd_group_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Add client-level role mappings to a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            roles: List of roles to map to the group
            
        Raises:
            APIError: If the mapping fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_groups_group_id_role_mappings_clients_client_id.asyncio_detailed,
            realm,
            group_id=group_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client role mappings: {response.status_code}")

    def remove_group_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level role mappings from a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            roles: List of roles to unmap from the group
            
        Raises:
            APIError: If the unmapping fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_groups_group_id_role_mappings_clients_client_id.sync_detailed,
            realm,
            group_id=group_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client role mappings: {response.status_code}")

    async def aremove_group_client_role_mappings(self, realm: str | None = None, *, group_id: str, client_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove client-level role mappings from a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            client_id: Client ID
            roles: List of roles to unmap from the group
            
        Raises:
            APIError: If the unmapping fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_groups_group_id_role_mappings_clients_client_id.asyncio_detailed,
            realm,
            group_id=group_id,
            client_id=client_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove client role mappings: {response.status_code}")


class ClientRoleMappingsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ClientRoleMappingsAPI."""
    
    @cached_property
    def client_role_mappings(self) -> ClientRoleMappingsAPI:
        """Get the ClientRoleMappingsAPI instance."""
        return ClientRoleMappingsAPI(manager=self)  # type: ignore[arg-type]