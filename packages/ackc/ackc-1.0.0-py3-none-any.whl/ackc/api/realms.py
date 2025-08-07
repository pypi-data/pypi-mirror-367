"""Realm management API methods."""
import json
from functools import cached_property
from io import BytesIO

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.realms_admin import (
    get_admin_realms,
    post_admin_realms,
    get_admin_realms_realm,
    put_admin_realms_realm,
    delete_admin_realms_realm,
    get_admin_realms_realm_events,
    delete_admin_realms_realm_events,
    get_admin_realms_realm_events_config,
    put_admin_realms_realm_events_config,
    get_admin_realms_realm_admin_events,
    delete_admin_realms_realm_admin_events,
    get_admin_realms_realm_default_groups,
    put_admin_realms_realm_default_groups_group_id,
    delete_admin_realms_realm_default_groups_group_id,
    get_admin_realms_realm_default_default_client_scopes,
    put_admin_realms_realm_default_default_client_scopes_client_scope_id,
    delete_admin_realms_realm_default_default_client_scopes_client_scope_id,
    get_admin_realms_realm_default_optional_client_scopes,
    put_admin_realms_realm_default_optional_client_scopes_client_scope_id,
    delete_admin_realms_realm_default_optional_client_scopes_client_scope_id,
    post_admin_realms_realm_partial_export,
    post_admin_realms_realm_partial_import,
    post_admin_realms_realm_logout_all,
    get_admin_realms_realm_client_session_stats,
)
from ..generated.models import (
    RealmRepresentation,
    AdminEventRepresentation,
    EventRepresentation,
    GroupRepresentation,
    ClientScopeRepresentation,
    RealmEventsConfigRepresentation,
)
from ..generated.types import File, UNSET, Unset

__all__ = (
    "RealmsAPI",
    "RealmsClientMixin",
    "RealmRepresentation",
    "AdminEventRepresentation",
    "EventRepresentation",
    "GroupRepresentation",
    "ClientScopeRepresentation",
    "RealmEventsConfigRepresentation",
)


class RealmsAPI(BaseAPI):
    """Realm management API methods."""

    def get_all(self) -> list[RealmRepresentation] | None:
        """List all realms (sync).
        
        Returns:
            List of all realms visible to the authenticated user
        """
        return self._sync_any(get_admin_realms.sync)

    async def aget_all(self) -> list[RealmRepresentation] | None:
        """List all realms (async).
        
        Returns:
            List of all realms visible to the authenticated user
        """
        return await self._async_any(get_admin_realms.asyncio)

    def create(self, realm_data: dict | RealmRepresentation) -> None:
        """Create a realm (sync).
        
        Args:
            realm_data: Realm configuration including name, settings, and attributes
            
        Raises:
            APIError: If realm creation fails
        """
        if isinstance(realm_data, RealmRepresentation):
            realm_dict = realm_data.to_dict()
        else:
            realm_dict = realm_data

        json_bytes = json.dumps(realm_dict).encode("utf-8")
        file_obj = File(
            payload=BytesIO(json_bytes),
            file_name="realm.json",
            mime_type="application/json"
        )

        response = self._sync_any(post_admin_realms.sync_detailed, body=file_obj)
        if response.status_code != 201:
            raise APIError(f"Failed to create realm: {response.status_code}")

    async def acreate(self, realm_data: dict | RealmRepresentation) -> None:
        """Create a realm (async).
        
        Args:
            realm_data: Realm configuration including name, settings, and attributes
            
        Raises:
            APIError: If realm creation fails
        """
        if isinstance(realm_data, RealmRepresentation):
            realm_dict = realm_data.to_dict()
        else:
            realm_dict = realm_data

        json_bytes = json.dumps(realm_dict).encode("utf-8")
        file_obj = File(
            payload=BytesIO(json_bytes),
            file_name="realm.json",
            mime_type="application/json"
        )

        response = await self._async_any(post_admin_realms.asyncio_detailed, body=file_obj)
        if response.status_code != 201:
            raise APIError(f"Failed to create realm: {response.status_code}")

    def get(self, realm: str) -> RealmRepresentation | None:
        """Get a realm (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            Realm representation with full details
        """
        return self._sync_any(get_admin_realms_realm.sync, realm=realm)

    async def aget(self, realm: str) -> RealmRepresentation | None:
        """Get a realm (async).
        
        Args:
            realm: The realm name
            
        Returns:
            Realm representation with full details
        """
        return await self._async_any(get_admin_realms_realm.asyncio, realm=realm)

    def update(self, realm: str, realm_data: dict | RealmRepresentation) -> None:
        """Update a realm (sync).
        
        Args:
            realm: The realm name
            realm_data: Updated realm configuration
            
        Raises:
            APIError: If realm update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm.sync_detailed,
            realm,
            realm_data,
            RealmRepresentation
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update realm: {response.status_code}")

    async def aupdate(self, realm: str, realm_data: dict | RealmRepresentation) -> None:
        """Update a realm (async).
        
        Args:
            realm: The realm name
            realm_data: Updated realm configuration
            
        Raises:
            APIError: If realm update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm.asyncio_detailed,
            realm,
            realm_data,
            RealmRepresentation
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update realm: {response.status_code}")

    def delete(self, realm: str) -> None:
        """Delete a realm (sync).
        
        Args:
            realm: The realm name to delete
            
        Raises:
            APIError: If realm deletion fails
        """
        response = self._sync_any(delete_admin_realms_realm.sync_detailed, realm=realm)
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete realm: {response.status_code}")

    async def adelete(self, realm: str) -> None:
        """Delete a realm (async).
        
        Args:
            realm: The realm name to delete
            
        Raises:
            APIError: If realm deletion fails
        """
        response = await self._async_any(delete_admin_realms_realm.asyncio_detailed, realm=realm)
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete realm: {response.status_code}")

    def get_events(
        self,
        realm: str | None = None,
        *,
        client_query: Unset | str = UNSET,
        date_from: Unset | str = UNSET,
        date_to: Unset | str = UNSET,
        direction: Unset | str = UNSET,
        first: Unset | int = UNSET,
        ip_address: Unset | str = UNSET,
        max: Unset | int = UNSET,
        type: Unset | list[str] = UNSET,
        user: Unset | str = UNSET
    ) -> list[EventRepresentation] | None:
        """Get realm events (sync).
        
        Args:
            realm: The realm name
            client_query: Filter by client ID
            date_from: Start date for event search
            date_to: End date for event search
            direction: Sort direction (asc or desc)
            first: Pagination offset
            ip_address: Filter by IP address
            max: Maximum results to return
            type: Filter by event types
            user: Filter by user ID
            
        Returns:
            List of realm events matching the filters
        """
        return self._sync(
            get_admin_realms_realm_events.sync,
            realm,
            client_query=client_query,
            date_from=date_from,
            date_to=date_to,
            direction=direction,
            first=first,
            ip_address=ip_address,
            max_=max,
            type_=type,
            user=user,
        )

    async def aget_events(
        self,
        realm: str | None = None,
        *,
        client_query: Unset | str = UNSET,
        date_from: Unset | str = UNSET,
        date_to: Unset | str = UNSET,
        direction: Unset | str = UNSET,
        first: Unset | int = UNSET,
        ip_address: Unset | str = UNSET,
        max: Unset | int = UNSET,
        type: Unset | list[str] = UNSET,
        user: Unset | str = UNSET
    ) -> list[EventRepresentation] | None:
        """Get realm events (async).
        
        Args:
            realm: The realm name
            client_query: Filter by client ID
            date_from: Start date for event search
            date_to: End date for event search
            direction: Sort direction (asc or desc)
            first: Pagination offset
            ip_address: Filter by IP address
            max: Maximum results to return
            type: Filter by event types
            user: Filter by user ID
            
        Returns:
            List of realm events matching the filters
        """
        return await self._async(
            get_admin_realms_realm_events.asyncio,
            realm,
            client_query=client_query,
            date_from=date_from,
            date_to=date_to,
            direction=direction,
            first=first,
            ip_address=ip_address,
            max_=max,
            type_=type,
            user=user,
        )

    def delete_events(self, realm: str | None = None) -> None:
        """Delete all realm events (sync).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If event deletion fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_events.sync_detailed,
            realm,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete events: {response.status_code}")

    async def adelete_events(self, realm: str | None = None) -> None:
        """Delete all realm events (async).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If event deletion fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_events.asyncio_detailed,
            realm,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete events: {response.status_code}")

    def get_admin_events(
        self,
        realm: str | None = None,
        *,
        auth_client: Unset | str = UNSET,
        auth_ip_address: Unset | str = UNSET,
        auth_realm: Unset | str = UNSET,
        auth_user: Unset | str = UNSET,
        date_from: Unset | str = UNSET,
        date_to: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        operation_types: Unset | list[str] = UNSET,
        resource_path: Unset | str = UNSET,
        resource_types: Unset | list[str] = UNSET
    ) -> list[AdminEventRepresentation] | None:
        """Get admin events (sync).
        
        Admin events track administrative actions like user creation or role changes.
        
        Args:
            realm: The realm name
            auth_client: Filter by authentication client
            auth_ip_address: Filter by authentication IP address
            auth_realm: Filter by authentication realm
            auth_user: Filter by authentication user
            date_from: Start date for event search
            date_to: End date for event search
            first: Pagination offset
            max: Maximum results to return
            operation_types: Filter by operation types
            resource_path: Filter by resource path
            resource_types: Filter by resource types
            
        Returns:
            List of admin events matching the filters
        """
        return self._sync(
            get_admin_realms_realm_admin_events.sync,
            realm,
            auth_client=auth_client,
            auth_ip_address=auth_ip_address,
            auth_realm=auth_realm,
            auth_user=auth_user,
            date_from=date_from,
            date_to=date_to,
            first=first,
            max_=max,
            operation_types=operation_types,
            resource_path=resource_path,
            resource_types=resource_types,
        )

    async def aget_admin_events(
        self,
        realm: str | None = None,
        *,
        auth_client: Unset | str = UNSET,
        auth_ip_address: Unset | str = UNSET,
        auth_realm: Unset | str = UNSET,
        auth_user: Unset | str = UNSET,
        date_from: Unset | str = UNSET,
        date_to: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        operation_types: Unset | list[str] = UNSET,
        resource_path: Unset | str = UNSET,
        resource_types: Unset | list[str] = UNSET
    ) -> list[AdminEventRepresentation] | None:
        """Get admin events (async).
        
        Admin events track administrative actions like user creation or role changes.
        
        Args:
            realm: The realm name
            auth_client: Filter by authentication client
            auth_ip_address: Filter by authentication IP address
            auth_realm: Filter by authentication realm
            auth_user: Filter by authentication user
            date_from: Start date for event search
            date_to: End date for event search
            first: Pagination offset
            max: Maximum results to return
            operation_types: Filter by operation types
            resource_path: Filter by resource path
            resource_types: Filter by resource types
            
        Returns:
            List of admin events matching the filters
        """
        return await self._async(
            get_admin_realms_realm_admin_events.asyncio,
            realm,
            auth_client=auth_client,
            auth_ip_address=auth_ip_address,
            auth_realm=auth_realm,
            auth_user=auth_user,
            date_from=date_from,
            date_to=date_to,
            first=first,
            max_=max,
            operation_types=operation_types,
            resource_path=resource_path,
            resource_types=resource_types,
        )

    def delete_admin_events(self, realm: str | None = None) -> None:
        """Delete all admin events (sync).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If admin event deletion fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_admin_events.sync_detailed,
            realm,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete admin events: {response.status_code}")

    async def adelete_admin_events(self, realm: str | None = None) -> None:
        """Delete all admin events (async).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If admin event deletion fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_admin_events.asyncio_detailed,
            realm,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete admin events: {response.status_code}")

    def get_events_config(self, realm: str | None = None) -> RealmEventsConfigRepresentation | None:
        """Get events configuration (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            Events configuration including enabled event types and settings
        """
        return self._sync(
            get_admin_realms_realm_events_config.sync,
            realm,
        )

    async def aget_events_config(self, realm: str | None = None) -> RealmEventsConfigRepresentation | None:
        """Get events configuration (async).
        
        Args:
            realm: The realm name
            
        Returns:
            Events configuration including enabled event types and settings
        """
        return await self._async(
            get_admin_realms_realm_events_config.asyncio,
            realm,
        )

    def update_events_config(self, realm: str | None = None, *, config: dict | RealmEventsConfigRepresentation) -> None:
        """Update events configuration (sync).
        
        Args:
            realm: The realm name
            config: Updated events configuration
            
        Raises:
            APIError: If configuration update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_events_config.sync_detailed,
            realm,
            config,
            RealmEventsConfigRepresentation
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update events config: {response.status_code}")

    async def aupdate_events_config(self, realm: str | None = None, *, config: dict | RealmEventsConfigRepresentation) -> None:
        """Update events configuration (async).
        
        Args:
            realm: The realm name
            config: Updated events configuration
            
        Raises:
            APIError: If configuration update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_events_config.asyncio_detailed,
            realm,
            config,
            RealmEventsConfigRepresentation
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update events config: {response.status_code}")

    def get_default_groups(self, realm: str | None = None) -> list[GroupRepresentation] | None:
        """Get default groups (sync).
        
        Default groups are automatically assigned to new users.
        
        Args:
            realm: The realm name
            
        Returns:
            List of default groups for the realm
        """
        return self._sync(
            get_admin_realms_realm_default_groups.sync,
            realm,
        )

    async def aget_default_groups(self, realm: str | None = None) -> list[GroupRepresentation] | None:
        """Get default groups (async).
        
        Default groups are automatically assigned to new users.
        
        Args:
            realm: The realm name
            
        Returns:
            List of default groups for the realm
        """
        return await self._async(
            get_admin_realms_realm_default_groups.asyncio,
            realm,
        )

    def add_default_group(self, realm: str | None = None, *, group_id: str) -> None:
        """Add default group (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID to add as default
            
        Raises:
            APIError: If adding default group fails
        """
        response = self._sync_detailed(
            put_admin_realms_realm_default_groups_group_id.sync_detailed,
            realm,
            group_id=group_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add default group: {response.status_code}")

    async def aadd_default_group(self, realm: str | None = None, *, group_id: str) -> None:
        """Add default group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID to add as default
            
        Raises:
            APIError: If adding default group fails
        """
        response = await self._async_detailed(
            put_admin_realms_realm_default_groups_group_id.asyncio_detailed,
            realm,
            group_id=group_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add default group: {response.status_code}")

    def remove_default_group(self, realm: str | None = None, *, group_id: str) -> None:
        """Remove default group (sync).
        
        Args:
            realm: The realm name
            group_id: Group ID to remove from defaults
            
        Raises:
            APIError: If removing default group fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_default_groups_group_id.sync_detailed,
            realm,
            group_id=group_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove default group: {response.status_code}")

    async def aremove_default_group(self, realm: str | None = None, *, group_id: str) -> None:
        """Remove default group (async).
        
        Args:
            realm: The realm name
            group_id: Group ID to remove from defaults
            
        Raises:
            APIError: If removing default group fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_default_groups_group_id.asyncio_detailed,
            realm,
            group_id=group_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove default group: {response.status_code}")

    def partial_export(
        self,
        realm: str | None = None,
        *,
        export_clients: bool = True,
        export_groups_and_roles: bool = True
    ) -> RealmRepresentation | None:
        """Partial export of realm (sync).
        
        Args:
            realm: The realm name
            export_clients: Whether to include clients in export
            export_groups_and_roles: Whether to include groups and roles in export
            
        Returns:
            Exported realm representation
        """
        return self._sync(
            post_admin_realms_realm_partial_export.sync,
            realm,
            export_clients=export_clients,
            export_groups_and_roles=export_groups_and_roles,
        )

    async def apartial_export(
        self,
        realm: str | None = None,
        *,
        export_clients: bool = True,
        export_groups_and_roles: bool = True
    ) -> RealmRepresentation | None:
        """Partial export of realm (async).
        
        Args:
            realm: The realm name
            export_clients: Whether to include clients in export
            export_groups_and_roles: Whether to include groups and roles in export
            
        Returns:
            Exported realm representation
        """
        return await self._async(
            post_admin_realms_realm_partial_export.asyncio,
            realm,
            export_clients=export_clients,
            export_groups_and_roles=export_groups_and_roles,
        )

    def partial_import(self, realm: str | None = None, *, rep: dict) -> None:
        """Partial import to realm (sync).
        
        Args:
            realm: The realm name
            rep: Realm representation to import
            
        Raises:
            APIError: If import fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_partial_import.sync_detailed,
            realm,
            body=rep,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to partial import: {response.status_code}")

    async def apartial_import(self, realm: str | None = None, *, rep: dict) -> None:
        """Partial import to realm (async).
        
        Args:
            realm: The realm name
            rep: Realm representation to import
            
        Raises:
            APIError: If import fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_partial_import.asyncio_detailed,
            realm,
            body=rep,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to partial import: {response.status_code}")

    def logout_all(self, realm: str | None = None) -> None:
        """Logout all sessions in realm (sync).
        
        Invalidates all user sessions in the realm.
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If logout operation fails
        """
        response = self._sync_detailed(
            post_admin_realms_realm_logout_all.sync_detailed,
            realm,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to logout all: {response.status_code}")

    async def alogout_all(self, realm: str | None = None) -> None:
        """Logout all sessions in realm (async).
        
        Invalidates all user sessions in the realm.
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If logout operation fails
        """
        response = await self._async_detailed(
            post_admin_realms_realm_logout_all.asyncio_detailed,
            realm,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to logout all: {response.status_code}")

    def get_client_session_stats(self, realm: str | None = None) -> list[dict[str, str]] | None:
        """Get client session statistics (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of client session statistics including active and offline sessions
        """
        return self._sync_ap_list(
            get_admin_realms_realm_client_session_stats.sync,
            realm,
        )

    async def aget_client_session_stats(self, realm: str | None = None) -> list[dict[str, str]] | None:
        """Get client session statistics (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of client session statistics including active and offline sessions
        """
        return await self._async_ap_list(
            get_admin_realms_realm_client_session_stats.asyncio,
            realm,
        )

    def get_default_client_scopes(self, realm: str | None = None) -> list[ClientScopeRepresentation] | None:
        """Get default client scopes (sync).
        
        Default client scopes are automatically assigned to new clients.
        
        Args:
            realm: The realm name
            
        Returns:
            List of default client scopes for the realm
        """
        return self._sync(
            get_admin_realms_realm_default_default_client_scopes.sync,
            realm,
        )

    async def aget_default_client_scopes(self, realm: str | None = None) -> list[ClientScopeRepresentation] | None:
        """Get default client scopes (async).
        
        Default client scopes are automatically assigned to new clients.
        
        Args:
            realm: The realm name
            
        Returns:
            List of default client scopes for the realm
        """
        return await self._async(
            get_admin_realms_realm_default_default_client_scopes.asyncio,
            realm,
        )

    def add_default_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Add default client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to add as default
            
        Raises:
            APIError: If adding default client scope fails
        """
        response = self._sync_detailed(
            put_admin_realms_realm_default_default_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add default client scope: {response.status_code}")

    async def aadd_default_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Add default client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to add as default
            
        Raises:
            APIError: If adding default client scope fails
        """
        response = await self._async_detailed(
            put_admin_realms_realm_default_default_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add default client scope: {response.status_code}")

    def remove_default_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Remove default client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to remove from defaults
            
        Raises:
            APIError: If removing default client scope fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_default_default_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove default client scope: {response.status_code}")

    async def aremove_default_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Remove default client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to remove from defaults
            
        Raises:
            APIError: If removing default client scope fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_default_default_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove default client scope: {response.status_code}")

    def get_optional_client_scopes(self, realm: str | None = None) -> list[ClientScopeRepresentation] | None:
        """Get optional client scopes (sync).
        
        Optional client scopes can be requested during authorization.
        
        Args:
            realm: The realm name
            
        Returns:
            List of optional client scopes for the realm
        """
        return self._sync(
            get_admin_realms_realm_default_optional_client_scopes.sync,
            realm,
        )

    async def aget_optional_client_scopes(self, realm: str | None = None) -> list[ClientScopeRepresentation] | None:
        """Get optional client scopes (async).
        
        Optional client scopes can be requested during authorization.
        
        Args:
            realm: The realm name
            
        Returns:
            List of optional client scopes for the realm
        """
        return await self._async(
            get_admin_realms_realm_default_optional_client_scopes.asyncio,
            realm,
        )

    def add_optional_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Add optional client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to add as optional
            
        Raises:
            APIError: If adding optional client scope fails
        """
        response = self._sync_detailed(
            put_admin_realms_realm_default_optional_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add optional client scope: {response.status_code}")

    async def aadd_optional_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Add optional client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to add as optional
            
        Raises:
            APIError: If adding optional client scope fails
        """
        response = await self._async_detailed(
            put_admin_realms_realm_default_optional_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add optional client scope: {response.status_code}")

    def remove_optional_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Remove optional client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to remove from optionals
            
        Raises:
            APIError: If removing optional client scope fails
        """
        response = self._sync_detailed(
            delete_admin_realms_realm_default_optional_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove optional client scope: {response.status_code}")

    async def aremove_optional_client_scope(self, realm: str | None = None, *, client_scope_id: str) -> None:
        """Remove optional client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID to remove from optionals
            
        Raises:
            APIError: If removing optional client scope fails
        """
        response = await self._async_detailed(
            delete_admin_realms_realm_default_optional_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove optional client scope: {response.status_code}")


class RealmsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the RealmsAPI."""

    @cached_property
    def realms(self) -> RealmsAPI:
        """Get the RealmsAPI instance.
        
        Returns:
            RealmsAPI instance for managing realms
        """
        return RealmsAPI(manager=self)  # type: ignore[arg-type]
