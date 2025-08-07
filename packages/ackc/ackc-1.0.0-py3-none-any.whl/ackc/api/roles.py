"""Role management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.roles import (
    get_admin_realms_realm_roles,
    post_admin_realms_realm_roles,
    get_admin_realms_realm_roles_role_name,
    put_admin_realms_realm_roles_role_name,
    delete_admin_realms_realm_roles_role_name,
    get_admin_realms_realm_roles_role_name_users,
    get_admin_realms_realm_roles_role_name_groups,
    get_admin_realms_realm_roles_role_name_composites,
    post_admin_realms_realm_roles_role_name_composites,
    delete_admin_realms_realm_roles_role_name_composites,
    get_admin_realms_realm_roles_role_name_composites_realm,
    get_admin_realms_realm_roles_role_name_composites_clients_client_uuid,
    get_admin_realms_realm_roles_role_name_management_permissions,
    put_admin_realms_realm_roles_role_name_management_permissions,
    get_admin_realms_realm_clients_client_uuid_roles,
    post_admin_realms_realm_clients_client_uuid_roles,
    get_admin_realms_realm_clients_client_uuid_roles_role_name,
    put_admin_realms_realm_clients_client_uuid_roles_role_name,
    delete_admin_realms_realm_clients_client_uuid_roles_role_name,
    get_admin_realms_realm_clients_client_uuid_roles_role_name_users,
    get_admin_realms_realm_clients_client_uuid_roles_role_name_composites,
    post_admin_realms_realm_clients_client_uuid_roles_role_name_composites,
    delete_admin_realms_realm_clients_client_uuid_roles_role_name_composites,
)
from ..generated.models import RoleRepresentation, UserRepresentation
from ..generated.types import UNSET, Unset

__all__ = "RolesAPI", "RolesClientMixin", "RoleRepresentation"


class RolesAPI(BaseAPI):
    """Role management API methods."""

    def get_all(
            self,
            realm: str | None = None,
            *,
            brief_representation: Unset | bool = True,
            first: Unset | int = UNSET,
            max: Unset | int = UNSET,
            search: Unset | str = '',
    ) -> list[RoleRepresentation] | None:
        """List realm roles.
        
        Args:
            realm: The realm name
            brief_representation: Only return basic role info (default True)
            first: Pagination offset
            max: Maximum results to return
            search: Search string for role name
            
        Returns:
            List of roles matching the filters
        """
        return self._sync(
            get_admin_realms_realm_roles.sync,
            realm,
            brief_representation=brief_representation,
            first=first,
            max_=max,
            search=search,
        )

    async def aget_all(
            self,
            realm: str | None = None,
            *,
            brief_representation: Unset | bool = True,
            first: Unset | int = UNSET,
            max: Unset | int = UNSET,
            search: Unset | str = '',
    ) -> list[RoleRepresentation] | None:
        """List realm roles (async).
        
        Args:
            realm: The realm name
            brief_representation: Only return basic role info (default True)
            first: Pagination offset
            max: Maximum results to return
            search: Search string for role name
            
        Returns:
            List of roles matching the filters
        """
        return await self._async(
            get_admin_realms_realm_roles.asyncio,
            realm,
            brief_representation=brief_representation,
            first=first,
            max_=max,
            search=search,
        )

    def create(self, realm: str | None = None, *, role_data: dict | RoleRepresentation) -> None:
        """Create a realm role (sync).
        
        Args:
            realm: The realm name
            role_data: Role configuration including name and description
            
        Raises:
            APIError: If role creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_roles.sync_detailed,
            realm,
            role_data,
            RoleRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create role: {response.status_code}")

    async def acreate(self, realm: str | None = None, *, role_data: dict | RoleRepresentation) -> None:
        """Create a realm role (async).
        
        Args:
            realm: The realm name
            role_data: Role configuration including name and description
            
        Raises:
            APIError: If role creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_roles.asyncio_detailed,
            realm,
            role_data,
            RoleRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create role: {response.status_code}")

    def get(self, realm: str | None = None, *, role_name: str) -> RoleRepresentation | None:
        """Get a role by name (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the role
            
        Returns:
            Role representation with full details
        """
        return self._sync(
            get_admin_realms_realm_roles_role_name.sync,
            realm,
            role_name=role_name
        )

    async def aget(self, realm: str | None = None, *, role_name: str) -> RoleRepresentation | None:
        """Get a role by name (async).
        
        Args:
            realm: The realm name
            role_name: Name of the role
            
        Returns:
            Role representation with full details
        """
        return await self._async(
            get_admin_realms_realm_roles_role_name.asyncio,
            realm,
            role_name=role_name
        )

    def update(self, realm: str | None = None, *, role_name: str, role_data: dict | RoleRepresentation) -> None:
        """Update a role (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the role to update
            role_data: Updated role configuration
            
        Raises:
            APIError: If role update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_roles_role_name.sync_detailed,
            realm,
            role_data,
            RoleRepresentation,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update role: {response.status_code}")

    async def aupdate(self, realm: str | None = None, *, role_name: str, role_data: dict | RoleRepresentation) -> None:
        """Update a role (async).
        
        Args:
            realm: The realm name
            role_name: Name of the role to update
            role_data: Updated role configuration
            
        Raises:
            APIError: If role update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_roles_role_name.asyncio_detailed,
            realm,
            role_data,
            RoleRepresentation,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update role: {response.status_code}")

    def delete(self, realm: str | None = None, *, role_name: str) -> None:
        """Delete a role (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the role to delete
            
        Raises:
            APIError: If role deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_roles_role_name.sync_detailed,
            realm,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete role: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, role_name: str) -> None:
        """Delete a role (async).
        
        Args:
            realm: The realm name
            role_name: Name of the role to delete
            
        Raises:
            APIError: If role deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_roles_role_name.asyncio_detailed,
            realm,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete role: {response.status_code}")

    def get_users(self, realm: str | None = None, *, role_name: str) -> list[UserRepresentation] | None:
        """Get users with this role (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the role
            
        Returns:
            List of users who have this role assigned
        """
        return self._sync(
            get_admin_realms_realm_roles_role_name_users.sync,
            realm,
            role_name=role_name
        )

    async def aget_users(self, realm: str | None = None, *, role_name: str) -> list[UserRepresentation] | None:
        """Get users with this role (async).
        
        Args:
            realm: The realm name
            role_name: Name of the role
            
        Returns:
            List of users who have this role assigned
        """
        return await self._async(
            get_admin_realms_realm_roles_role_name_users.asyncio,
            realm,
            role_name=role_name
        )

    def get_groups(
        self,
        realm: str | None = None,
        *,
        role_name: str,
        brief_representation: Unset | bool = True,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET
    ) -> list[UserRepresentation] | None:
        """Get groups with this role (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the role
            brief_representation: Only return basic group info (default True)
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of groups that have this role assigned

        NOTE: The return type of this is suspicious, as it returns UserRepresentation objects instead of GroupRepresentation.
        TODO: Report incorrect return type in the API documentation.
        """
        return self._sync(
            get_admin_realms_realm_roles_role_name_groups.sync,
            realm,
            role_name=role_name,
            brief_representation=brief_representation,
            first=first,
            max_=max
        )

    async def aget_groups(
        self,
        realm: str | None = None, *,
        role_name: str, brief_representation: Unset | bool = True,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET
    ) -> list[UserRepresentation] | None:
        """Get groups with this role (async).
        
        Args:
            realm: The realm name
            role_name: Name of the role
            brief_representation: Only return basic group info (default True)
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of groups that have this role assigned

        NOTE: The return type of this is suspicious, as it returns UserRepresentation objects instead of GroupRepresentation.
        TODO: Report incorrect return type in the API documentation.
        """
        return await self._async(
            get_admin_realms_realm_roles_role_name_groups.asyncio,
            realm,
            role_name=role_name,
            brief_representation=brief_representation,
            first=first,
            max_=max
        )

    def get_composites(self, realm: str | None = None, *, role_name: str) -> list[RoleRepresentation] | None:
        """Get composite roles (sync).
        
        Composite roles contain other roles as children.
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            
        Returns:
            List of child roles contained in this composite role
        """
        return self._sync(
            get_admin_realms_realm_roles_role_name_composites.sync,
            realm,
            role_name=role_name
        )

    async def aget_composites(self, realm: str | None = None, *, role_name: str) -> list[RoleRepresentation] | None:
        """Get composite roles (async).
        
        Composite roles contain other roles as children.
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            
        Returns:
            List of child roles contained in this composite role
        """
        return await self._async(
            get_admin_realms_realm_roles_role_name_composites.asyncio,
            realm,
            role_name=role_name
        )

    def add_composites(self, realm: str | None = None, *, role_name: str, roles: list[RoleRepresentation]) -> None:
        """Add composite roles (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            roles: List of child roles to add
            
        Raises:
            APIError: If adding composite roles fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_roles_role_name_composites.sync_detailed,
            realm,
            role_name=role_name,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add composite roles: {response.status_code}")

    async def aadd_composites(self, realm: str | None = None, *, role_name: str, roles: list[RoleRepresentation]) -> None:
        """Add composite roles (async).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            roles: List of child roles to add
            
        Raises:
            APIError: If adding composite roles fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_roles_role_name_composites.asyncio_detailed,
            realm,
            role_name=role_name,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add composite roles: {response.status_code}")

    def remove_composites(self, realm: str | None = None, *, role_name: str, roles: list[RoleRepresentation]) -> None:
        """Remove composite roles (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            roles: List of child roles to remove
            
        Raises:
            APIError: If removing composite roles fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_roles_role_name_composites.sync_detailed,
            realm,
            role_name=role_name,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove composite roles: {response.status_code}")

    async def aremove_composites(self, realm: str | None = None, *, role_name: str, roles: list[RoleRepresentation]) -> None:
        """Remove composite roles (async).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            roles: List of child roles to remove
            
        Raises:
            APIError: If removing composite roles fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_roles_role_name_composites.asyncio_detailed,
            realm,
            role_name=role_name,
            body=roles
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove composite roles: {response.status_code}")

    def get_realm_composites(self, realm: str | None = None, *, role_name: str) -> list[RoleRepresentation] | None:
        """Get realm-level composite roles (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            
        Returns:
            List of realm-level child roles in this composite
        """
        return self._sync(
            get_admin_realms_realm_roles_role_name_composites_realm.sync,
            realm,
            role_name=role_name
        )

    async def aget_realm_composites(self, realm: str | None = None, *, role_name: str) -> list[RoleRepresentation] | None:
        """Get realm-level composite roles (async).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            
        Returns:
            List of realm-level child roles in this composite
        """
        return await self._async(
            get_admin_realms_realm_roles_role_name_composites_realm.asyncio,
            realm,
            role_name=role_name
        )

    def get_client_composites(
            self,
            realm: str | None = None,
            *,
            role_name: str,
            client_uuid: str
    ) -> list[RoleRepresentation] | None:
        """Get client-level composite roles (sync).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            client_uuid: Client UUID for client-level roles
            
        Returns:
            List of client-level child roles in this composite
        """
        return self._sync(
            get_admin_realms_realm_roles_role_name_composites_clients_client_uuid.sync,
            realm,
            role_name=role_name,
            client_uuid=client_uuid
        )

    async def aget_client_composites(
            self,
            realm: str | None = None,
            *,
            role_name: str,
            client_uuid: str
    ) -> list[RoleRepresentation] | None:
        """Get client-level composite roles (async).
        
        Args:
            realm: The realm name
            role_name: Name of the parent role
            client_uuid: Client UUID for client-level roles
            
        Returns:
            List of client-level child roles in this composite
        """
        return await self._async(
            get_admin_realms_realm_roles_role_name_composites_clients_client_uuid.asyncio,
            realm,
            role_name=role_name,
            client_uuid=client_uuid
        )

    # Client Roles
    def get_client_roles(self, realm: str | None = None, *, client_uuid: str) -> list[RoleRepresentation] | None:
        """Get all client roles (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of all roles defined for the client
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_roles.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_roles(self, realm: str | None = None, *, client_uuid: str) -> list[RoleRepresentation] | None:
        """Get all client roles (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of all roles defined for the client
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_roles.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def create_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_data: dict | RoleRepresentation
    ) -> None:
        """Create a client role (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_data: Role configuration including name and description
            
        Raises:
            APIError: If client role creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_roles.sync_detailed,
            realm,
            role_data,
            RoleRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client role: {response.status_code}")

    async def acreate_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_data: dict | RoleRepresentation
    ) -> None:
        """Create a client role (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_data: Role configuration including name and description
            
        Raises:
            APIError: If client role creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_roles.asyncio_detailed,
            realm,
            role_data,
            RoleRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client role: {response.status_code}")

    def get_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str
    ) -> RoleRepresentation | None:
        """Get a client role (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role
            
        Returns:
            Client role representation with full details
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_roles_role_name.sync,
            realm,
            client_uuid=client_uuid,
            role_name=role_name
        )

    async def aget_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str
    ) -> RoleRepresentation | None:
        """Get a client role (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role
            
        Returns:
            Client role representation with full details
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_roles_role_name.asyncio,
            realm,
            client_uuid=client_uuid,
            role_name=role_name
        )

    def update_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str,
            role_data: dict | RoleRepresentation
    ) -> None:
        """Update a client role (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role to update
            role_data: Updated role configuration
            
        Raises:
            APIError: If client role update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid_roles_role_name.sync_detailed,
            realm,
            role_data,
            RoleRepresentation,
            client_uuid=client_uuid,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client role: {response.status_code}")

    async def aupdate_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str,
            role_data: dict | RoleRepresentation
    ) -> None:
        """Update a client role (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role to update
            role_data: Updated role configuration
            
        Raises:
            APIError: If client role update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid_roles_role_name.asyncio_detailed,
            realm,
            role_data,
            RoleRepresentation,
            client_uuid=client_uuid,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client role: {response.status_code}")

    def delete_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str
    ) -> None:
        """Delete a client role (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role to delete
            
        Raises:
            APIError: If client role deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_roles_role_name.sync_detailed,
            realm,
            client_uuid=client_uuid,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client role: {response.status_code}")

    async def adelete_client_role(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str
    ) -> None:
        """Delete a client role (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role to delete
            
        Raises:
            APIError: If client role deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_roles_role_name.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            role_name=role_name
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client role: {response.status_code}")

    def get_client_role_users(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str
    ) -> list[UserRepresentation] | None:
        """Get users with client role (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role
            
        Returns:
            List of users who have this client role assigned
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_roles_role_name_users.sync,
            realm,
            client_uuid=client_uuid,
            role_name=role_name
        )

    async def aget_client_role_users(
            self,
            realm: str | None = None,
            *,
            client_uuid: str,
            role_name: str
    ) -> list[UserRepresentation] | None:
        """Get users with client role (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            role_name: Name of the role
            
        Returns:
            List of users who have this client role assigned
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_roles_role_name_users.asyncio,
            realm,
            client_uuid=client_uuid,
            role_name=role_name
        )


class RolesClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the RolesAPI."""

    @cached_property
    def roles(self) -> RolesAPI:
        """Get the RolesAPI instance.
        
        Returns:
            RolesAPI instance for managing roles
        """
        return RolesAPI(manager=self)  # type: ignore[arg-type]
