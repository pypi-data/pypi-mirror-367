"""Role mapper API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.role_mapper import (
    get_admin_realms_realm_users_user_id_role_mappings,
    get_admin_realms_realm_users_user_id_role_mappings_realm,
    get_admin_realms_realm_users_user_id_role_mappings_realm_available,
    get_admin_realms_realm_users_user_id_role_mappings_realm_composite,
    post_admin_realms_realm_users_user_id_role_mappings_realm,
    delete_admin_realms_realm_users_user_id_role_mappings_realm,
    get_admin_realms_realm_groups_group_id_role_mappings,
    get_admin_realms_realm_groups_group_id_role_mappings_realm,
    get_admin_realms_realm_groups_group_id_role_mappings_realm_available,
    get_admin_realms_realm_groups_group_id_role_mappings_realm_composite,
    post_admin_realms_realm_groups_group_id_role_mappings_realm,
    delete_admin_realms_realm_groups_group_id_role_mappings_realm,
)
from ..generated.models import MappingsRepresentation, RoleRepresentation
from ..generated.types import UNSET, Unset

__all__ = "RoleMapperAPI", "RoleMapperClientMixin"


class RoleMapperAPI(BaseAPI):
    """Role mapper API methods."""

    def get_user_role_mappings(self, realm: str | None = None, *, user_id: str) -> MappingsRepresentation | None:
        """Get all role mappings for a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            Complete role mappings including realm and client roles
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings.sync,
            realm,
            user_id=user_id
        )

    async def aget_user_role_mappings(self, realm: str | None = None, *, user_id: str) -> MappingsRepresentation | None:
        """Get all role mappings for a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            Complete role mappings including realm and client roles
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings.asyncio,
            realm,
            user_id=user_id
        )

    def get_user_realm_role_mappings(self, realm: str | None = None, *, user_id: str) -> list[RoleRepresentation] | None:
        """Get realm-level role mappings for a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of realm roles mapped to the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings_realm.sync,
            realm,
            user_id=user_id
        )

    async def aget_user_realm_role_mappings(self, realm: str | None = None, *, user_id: str) -> list[RoleRepresentation] | None:
        """Get realm-level role mappings for a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of realm roles mapped to the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings_realm.asyncio,
            realm,
            user_id=user_id
        )

    def get_user_available_realm_role_mappings(self, realm: str | None = None, *, user_id: str) -> list[RoleRepresentation] | None:
        """Get available realm-level role mappings for a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of realm roles that can be mapped to the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings_realm_available.sync,
            realm,
            user_id=user_id
        )

    async def aget_user_available_realm_role_mappings(self, realm: str | None = None, *, user_id: str) -> list[RoleRepresentation] | None:
        """Get available realm-level role mappings for a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of realm roles that can be mapped to the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings_realm_available.asyncio,
            realm,
            user_id=user_id
        )

    def get_user_composite_realm_role_mappings(self, realm: str | None = None, *, user_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level role mappings for a user.
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            user_id: User ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective realm roles for the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_role_mappings_realm_composite.sync,
            realm,
            user_id=user_id,
            brief_representation=brief_representation
        )

    async def aget_user_composite_realm_role_mappings(self, realm: str | None = None, *, user_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level role mappings for a user (async).
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            user_id: User ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective realm roles for the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_role_mappings_realm_composite.asyncio,
            realm,
            user_id=user_id,
            brief_representation=brief_representation
        )

    def add_user_realm_role_mappings(self, realm: str | None = None, *, user_id: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level role mappings to a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            roles: List of realm roles to map to the user
            
        Raises:
            APIError: If the mapping fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_users_user_id_role_mappings_realm.sync_detailed,
            realm,
            user_id=user_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm role mappings: {response.status_code}")

    async def aadd_user_realm_role_mappings(self, realm: str | None = None, *, user_id: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level role mappings to a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            roles: List of realm roles to map to the user
            
        Raises:
            APIError: If the mapping fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_users_user_id_role_mappings_realm.asyncio_detailed,
            realm,
            user_id=user_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm role mappings: {response.status_code}")

    def remove_user_realm_role_mappings(self, realm: str | None = None, *, user_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level role mappings from a user.
        
        Args:
            realm: The realm name
            user_id: User ID
            roles: List of realm roles to unmap from the user
            
        Raises:
            APIError: If the unmapping fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_users_user_id_role_mappings_realm.sync_detailed,
            realm,
            user_id=user_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm role mappings: {response.status_code}")

    async def aremove_user_realm_role_mappings(self, realm: str | None = None, *, user_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level role mappings from a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            roles: List of realm roles to unmap from the user
            
        Raises:
            APIError: If the unmapping fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_users_user_id_role_mappings_realm.asyncio_detailed,
            realm,
            user_id=user_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm role mappings: {response.status_code}")

    def get_group_role_mappings(self, realm: str | None = None, *, group_id: str) -> MappingsRepresentation | None:
        """Get all role mappings for a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            Complete role mappings including realm and client roles
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings.sync,
            realm,
            group_id=group_id
        )

    async def aget_group_role_mappings(self, realm: str | None = None, *, group_id: str) -> MappingsRepresentation | None:
        """Get all role mappings for a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            Complete role mappings including realm and client roles
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings.asyncio,
            realm,
            group_id=group_id
        )

    def get_group_realm_role_mappings(self, realm: str | None = None, *, group_id: str) -> list[RoleRepresentation] | None:
        """Get realm-level role mappings for a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            List of realm roles mapped to the group
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings_realm.sync,
            realm,
            group_id=group_id
        )

    async def aget_group_realm_role_mappings(self, realm: str | None = None, *, group_id: str) -> list[RoleRepresentation] | None:
        """Get realm-level role mappings for a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            List of realm roles mapped to the group
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings_realm.asyncio,
            realm,
            group_id=group_id
        )

    def get_group_available_realm_role_mappings(self, realm: str | None = None, *, group_id: str) -> list[RoleRepresentation] | None:
        """Get available realm-level role mappings for a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            List of realm roles that can be mapped to the group
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings_realm_available.sync,
            realm,
            group_id=group_id
        )

    async def aget_group_available_realm_role_mappings(self, realm: str | None = None, *, group_id: str) -> list[RoleRepresentation] | None:
        """Get available realm-level role mappings for a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            List of realm roles that can be mapped to the group
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings_realm_available.asyncio,
            realm,
            group_id=group_id
        )

    def get_group_composite_realm_role_mappings(self, realm: str | None = None, *, group_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level role mappings for a group.
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            group_id: Group ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective realm roles for the group
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_role_mappings_realm_composite.sync,
            realm,
            group_id=group_id,
            brief_representation=brief_representation
        )

    async def aget_group_composite_realm_role_mappings(self, realm: str | None = None, *, group_id: str, brief_representation: Unset | bool = True) -> list[RoleRepresentation] | None:
        """Get composite realm-level role mappings for a group (async).
        
        Includes roles mapped directly and through composite roles.
        
        Args:
            realm: The realm name
            group_id: Group ID
            brief_representation: Return brief representation (default True)
            
        Returns:
            List of effective realm roles for the group
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_role_mappings_realm_composite.asyncio,
            realm,
            group_id=group_id,
            brief_representation=brief_representation
        )

    def add_group_realm_role_mappings(self, realm: str | None = None, *, group_id: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level role mappings to a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            roles: List of realm roles to map to the group
            
        Raises:
            APIError: If the mapping fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_groups_group_id_role_mappings_realm.sync_detailed,
            realm,
            group_id=group_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm role mappings: {response.status_code}")

    async def aadd_group_realm_role_mappings(self, realm: str | None = None, *, group_id: str, roles: list[RoleRepresentation]) -> None:
        """Add realm-level role mappings to a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            roles: List of realm roles to map to the group
            
        Raises:
            APIError: If the mapping fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_groups_group_id_role_mappings_realm.asyncio_detailed,
            realm,
            group_id=group_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add realm role mappings: {response.status_code}")

    def remove_group_realm_role_mappings(self, realm: str | None = None, *, group_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level role mappings from a group.
        
        Args:
            realm: The realm name
            group_id: Group ID
            roles: List of realm roles to unmap from the group
            
        Raises:
            APIError: If the unmapping fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_groups_group_id_role_mappings_realm.sync_detailed,
            realm,
            group_id=group_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm role mappings: {response.status_code}")

    async def aremove_group_realm_role_mappings(self, realm: str | None = None, *, group_id: str, roles: list[RoleRepresentation]) -> None:
        """Remove realm-level role mappings from a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            roles: List of realm roles to unmap from the group
            
        Raises:
            APIError: If the unmapping fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_groups_group_id_role_mappings_realm.asyncio_detailed,
            realm,
            group_id=group_id,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove realm role mappings: {response.status_code}")


class RoleMapperClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the RoleMapperAPI."""
    
    @cached_property
    def role_mapper(self) -> RoleMapperAPI:
        """Get the RoleMapperAPI instance."""
        return RoleMapperAPI(manager=self)  # type: ignore[arg-type]