"""Group management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.groups import (
    get_admin_realms_realm_groups,
    get_admin_realms_realm_groups_count,
    post_admin_realms_realm_groups,
    get_admin_realms_realm_groups_group_id,
    put_admin_realms_realm_groups_group_id,
    delete_admin_realms_realm_groups_group_id,
    get_admin_realms_realm_groups_group_id_members,
    get_admin_realms_realm_groups_group_id_children,
    post_admin_realms_realm_groups_group_id_children,
    get_admin_realms_realm_groups_group_id_management_permissions,
    put_admin_realms_realm_groups_group_id_management_permissions,
)
from ..generated.models import GroupRepresentation, ManagementPermissionReference, UserRepresentation
from ..generated.types import UNSET, Unset

__all__ = "GroupsAPI", "GroupsClientMixin", "GroupRepresentation"


class GroupsAPI(BaseAPI):
    """Group management API methods."""

    def get_all(
        self,
        realm: str | None = None,
        *,
        brief_representation: Unset | bool = True,
        exact: Unset | bool = False,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        populate_hierarchy: Unset | bool = True,
        q: Unset | str = UNSET,
        search: Unset | str = UNSET,
        sub_groups_count: Unset | bool = True,
    ) -> list[GroupRepresentation] | None:
        """List groups in a realm.
        
        Args:
            realm: The realm name
            brief_representation: Only return basic group info (default True)
            exact: Exact match for searches
            first: Pagination offset
            max: Maximum results to return
            populate_hierarchy: Include full group hierarchy
            q: Query string for group search
            search: Search string (searches group name)
            sub_groups_count: Include subgroup count (default True)
            
        Returns:
            List of groups matching the filters
        """
        return self._sync(
            get_admin_realms_realm_groups.sync,
            realm,
            brief_representation=brief_representation,
            exact=exact,
            first=first,
            max_=max,
            populate_hierarchy=populate_hierarchy,
            q=q,
            search=search,
            sub_groups_count=sub_groups_count,
        )

    async def aget_all(
        self,
        realm: str | None = None,
        *,
        brief_representation: Unset | bool = True,
        exact: Unset | bool = False,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        populate_hierarchy: Unset | bool = True,
        q: Unset | str = UNSET,
        search: Unset | str = UNSET,
        sub_groups_count: Unset | bool = True,
    ) -> list[GroupRepresentation] | None:
        """List groups in a realm (async).
        
        Args:
            realm: The realm name
            brief_representation: Only return basic group info (default True)
            exact: Exact match for searches
            first: Pagination offset
            max: Maximum results to return
            populate_hierarchy: Include full group hierarchy
            q: Query string for group search
            search: Search string (searches group name)
            sub_groups_count: Include subgroup count (default True)
            
        Returns:
            List of groups matching the filters
        """
        return await self._async(
            get_admin_realms_realm_groups.asyncio,
            realm,
            brief_representation=brief_representation,
            exact=exact,
            first=first,
            max_=max,
            populate_hierarchy=populate_hierarchy,
            q=q,
            search=search,
            sub_groups_count=sub_groups_count,
        )

    def create(self, realm: str | None = None, *, group_data: dict | GroupRepresentation) -> str:
        """Create a group (sync).
        
        Args:
            realm: The realm name
            group_data: Group configuration including name and path
            
        Returns:
            Created group ID
            
        Raises:
            APIError: If group creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_groups.sync_detailed,
            realm,
            group_data,
            GroupRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create group: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def acreate(self, realm: str | None = None, *, group_data: dict | GroupRepresentation) -> str:
        """Create a group (async).
        
        Args:
            realm: The realm name
            group_data: Group configuration including name and path
            
        Returns:
            Created group ID
            
        Raises:
            APIError: If group creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_groups.asyncio_detailed,
            realm,
            group_data,
            GroupRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create group: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def get(self, realm: str | None = None, *, group_id: str) -> GroupRepresentation | None:
        """Get a group by ID (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            Group representation with full details
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id.sync,
            realm,
            group_id=group_id
        )

    async def aget(self, realm: str | None = None, *, group_id: str) -> GroupRepresentation | None:
        """Get a group by ID (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            Group representation with full details
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id.asyncio,
            realm,
            group_id=group_id
        )

    def update(self, realm: str | None = None, *, group_id: str, group_data: dict | GroupRepresentation) -> None:
        """Update a group (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID to update
            group_data: Updated group configuration
            
        Raises:
            APIError: If group update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_groups_group_id.sync_detailed,
            realm,
            group_data,
            GroupRepresentation,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update group: {response.status_code}")

    async def aupdate(self, realm: str | None = None, *, group_id: str, group_data: dict | GroupRepresentation) -> None:
        """Update a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID to update
            group_data: Updated group configuration
            
        Raises:
            APIError: If group update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_groups_group_id.asyncio_detailed,
            realm,
            group_data,
            GroupRepresentation,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update group: {response.status_code}")

    def delete(self, realm: str | None = None, *, group_id: str) -> None:
        """Delete a group (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID to delete
            
        Raises:
            APIError: If group deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_groups_group_id.sync_detailed,
            realm,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete group: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, group_id: str) -> None:
        """Delete a group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID to delete
            
        Raises:
            APIError: If group deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_groups_group_id.asyncio_detailed,
            realm,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete group: {response.status_code}")

    def get_members(
        self,
        realm: str | None = None,
        *,
        group_id: str,
        brief_representation: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
    ) -> list[UserRepresentation] | None:
        """Get group members (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID
            brief_representation: Return brief representation
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of users who are members of the group
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_members.sync,
            realm,
            group_id=group_id,
            brief_representation=brief_representation,
            first=first,
            max_=max,
        )

    async def aget_members(
        self,
        realm: str | None = None,
        *,
        group_id: str,
        brief_representation: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
    ) -> list[UserRepresentation] | None:
        """Get group members (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            brief_representation: Return brief representation
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of users who are members of the group
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_members.asyncio,
            realm,
            group_id=group_id,
            brief_representation=brief_representation,
            first=first,
            max_=max,
        )

    def get_count(self, realm: str | None = None, *, search: str | None = None, top: bool = False) -> int | None:
        """Get total group count (sync).
        
        Args:
            realm: The realm name
            search: Optional search string to filter groups
            top: If True, only count top-level groups
            
        Returns:
            Total number of groups matching criteria
        """
        result = self._sync_ap(
            get_admin_realms_realm_groups_count.sync,
            realm,
            search=search,
            top=top,
        )
        return result.get("count") if result else None

    async def aget_count(self, realm: str | None = None, *, search: str | None = None, top: bool = False) -> int | None:
        """Get total group count (async).
        
        Args:
            realm: The realm name
            search: Optional search string to filter groups
            top: If True, only count top-level groups
            
        Returns:
            Total number of groups matching criteria
        """
        result = await self._async_ap(
            get_admin_realms_realm_groups_count.asyncio,
            realm,
            search=search,
            top=top,
        )
        return result.get("count") if result else None

    def get_children(self, realm: str | None = None, *, group_id: str, brief_representation: Unset | bool = False, exact: Unset | bool = UNSET, first: Unset | int = 0, max_results: Unset | int = 10, search: Unset | str = UNSET, sub_groups_count: Unset | bool = True) -> list[GroupRepresentation] | None:
        """Get child groups (sync).
        
        Args:
            realm: The realm name
            group_id: Parent group ID
            brief_representation: Return brief representation (default False)
            exact: Exact match for searches
            first: Pagination offset (default 0)
            max_results: Maximum results to return (default 10)
            search: Search string
            sub_groups_count: Include subgroup count (default True)
            
        Returns:
            List of child groups
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_children.sync,
            realm,
            group_id=group_id,
            brief_representation=brief_representation,
            exact=exact,
            first=first,
            max_=max_results,
            search=search,
            sub_groups_count=sub_groups_count,
        )

    async def aget_children(self, realm: str | None = None, *, group_id: str, brief_representation: Unset | bool = False, exact: Unset | bool = UNSET, first: Unset | int = 0, max_results: Unset | int = 10, search: Unset | str = UNSET, sub_groups_count: Unset | bool = True) -> list[GroupRepresentation] | None:
        """Get child groups (async).
        
        Args:
            realm: The realm name
            group_id: Parent group ID
            brief_representation: Return brief representation (default False)
            exact: Exact match for searches
            first: Pagination offset (default 0)
            max_results: Maximum results to return (default 10)
            search: Search string
            sub_groups_count: Include subgroup count (default True)
            
        Returns:
            List of child groups
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_children.asyncio,
            realm,
            group_id=group_id,
            brief_representation=brief_representation,
            exact=exact,
            first=first,
            max_=max_results,
            search=search,
            sub_groups_count=sub_groups_count,
        )

    def add_child(self, realm: str | None = None, *, group_id: str, child_data: dict | GroupRepresentation) -> str:
        """Add a child group (sync).
        
        Creates a new group as a child of the specified parent group.
        
        Args:
            realm: The realm name
            group_id: Parent group ID
            child_data: Child group configuration
            
        Returns:
            Created child group ID
            
        Raises:
            APIError: If child group creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_groups_group_id_children.sync_detailed,
            realm,
            child_data,
            GroupRepresentation,
            group_id=group_id
        )
        if response.status_code != 201:
            raise APIError(f"Failed to add child group: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def aadd_child(self, realm: str | None = None, *, group_id: str, child_data: dict | GroupRepresentation) -> str:
        """Add a child group (async).
        
        Creates a new group as a child of the specified parent group.
        
        Args:
            realm: The realm name
            group_id: Parent group ID
            child_data: Child group configuration
            
        Returns:
            Created child group ID
            
        Raises:
            APIError: If child group creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_groups_group_id_children.asyncio_detailed,
            realm,
            child_data,
            GroupRepresentation,
            group_id=group_id
        )
        if response.status_code != 201:
            raise APIError(f"Failed to add child group: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def get_management_permissions(self, realm: str | None = None, *, group_id: str) -> ManagementPermissionReference | None:
        """Get management permissions for group (sync).
        
        Returns whether group authorization permissions have been initialized.
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            Management permission reference
        """
        return self._sync(
            get_admin_realms_realm_groups_group_id_management_permissions.sync,
            realm,
            group_id=group_id
        )

    async def aget_management_permissions(self, realm: str | None = None, *, group_id: str) -> ManagementPermissionReference | None:
        """Get management permissions for group (async).
        
        Returns whether group authorization permissions have been initialized.
        
        Args:
            realm: The realm name
            group_id: Group ID
            
        Returns:
            Management permission reference
        """
        return await self._async(
            get_admin_realms_realm_groups_group_id_management_permissions.asyncio,
            realm,
            group_id=group_id
        )

    def update_management_permissions(self, realm: str | None = None, *, group_id: str, permissions: dict | ManagementPermissionReference) -> ManagementPermissionReference | None:
        """Update management permissions for group (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID
            permissions: Management permissions to set
            
        Returns:
            Updated management permission reference
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_groups_group_id_management_permissions.sync_detailed,
            realm,
            permissions,
            ManagementPermissionReference,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update management permissions: {response.status_code}")
        return response.parsed

    async def aupdate_management_permissions(self, realm: str | None = None, *, group_id: str, permissions: dict | ManagementPermissionReference) -> ManagementPermissionReference | None:
        """Update management permissions for group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID
            permissions: Management permissions to set
            
        Returns:
            Updated management permission reference
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_groups_group_id_management_permissions.asyncio_detailed,
            realm,
            permissions,
            ManagementPermissionReference,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update management permissions: {response.status_code}")
        return response.parsed


class GroupsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the GroupsAPI.
    """

    @cached_property
    def groups(self) -> GroupsAPI:
        """Get the GroupsAPI instance."""
        return GroupsAPI(manager=self)  # type: ignore[arg-type]
