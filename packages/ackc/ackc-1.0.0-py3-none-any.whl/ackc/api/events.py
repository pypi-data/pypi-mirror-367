"""Events management API methods."""
from datetime import datetime
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.realms_admin import (
    get_admin_realms_realm_events,
    delete_admin_realms_realm_events,
    get_admin_realms_realm_admin_events,
    delete_admin_realms_realm_admin_events,
    get_admin_realms_realm_events_config,
    put_admin_realms_realm_events_config,
)
from ..generated.models import (
    RealmEventsConfigRepresentation,
    EventRepresentation,
    AdminEventRepresentation,
)
from ..generated.types import UNSET, Unset

__all__ = (
    "EventsAPI", 
    "EventsClientMixin",
    "RealmEventsConfigRepresentation",
    "EventRepresentation", 
    "AdminEventRepresentation",
)


class EventsAPI(BaseAPI):
    """Events management API methods for auditing user and admin actions."""

    def get_events(
        self, 
        realm: str | None = None, 
        *,
        client: Unset | str = UNSET,
        date_from: Unset | str | datetime = UNSET,
        date_to: Unset | str | datetime = UNSET,
        direction: Unset | str = UNSET,
        first: Unset | int = UNSET,
        ip_address: Unset | str = UNSET,
        max: Unset | int = UNSET,
        type: Unset | list[str] | str = UNSET,
        user: Unset | str = UNSET,
    ) -> list[EventRepresentation] | None:
        """Get user events from the event store.
        
        Args:
            realm: The realm name
            client: Filter by client ID
            date_from: From date in ISO format (e.g., "2023-01-01") or datetime object
            date_to: To date in ISO format or datetime object
            direction: Sort direction ("ASC" or "DESC")
            first: Pagination offset
            ip_address: Filter by IP address
            max: Maximum results to return (default 100)
            type: Event type(s) to filter by - can be a single string or list
            user: Filter by user ID
            
        Returns:
            List of user events matching the filters
        """
        if isinstance(date_from, datetime):
            date_from = date_from.isoformat()
        if isinstance(date_to, datetime):
            date_to = date_to.isoformat()
        if isinstance(type, str):
            type = [type]
            
        return self._sync(
            get_admin_realms_realm_events.sync, 
            realm,
            client_query=client,
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
        client: Unset | str = UNSET,
        date_from: Unset | str | datetime = UNSET,
        date_to: Unset | str | datetime = UNSET,
        direction: Unset | str = UNSET,
        first: Unset | int = UNSET,
        ip_address: Unset | str = UNSET,
        max: Unset | int = UNSET,
        type: Unset | list[str] | str = UNSET,
        user: Unset | str = UNSET,
    ) -> list[EventRepresentation] | None:
        """Get user events from the event store (async).
        
        Args:
            realm: The realm name
            client: Filter by client ID
            date_from: From date in ISO format (e.g., "2023-01-01") or datetime object
            date_to: To date in ISO format or datetime object
            direction: Sort direction ("ASC" or "DESC")
            first: Pagination offset
            ip_address: Filter by IP address
            max: Maximum results to return (default 100)
            type: Event type(s) to filter by - can be a single string or list
            user: Filter by user ID
            
        Returns:
            List of user events matching the filters
        """
        if isinstance(date_from, datetime):
            date_from = date_from.isoformat()
        if isinstance(date_to, datetime):
            date_to = date_to.isoformat()
        if isinstance(type, str):
            type = [type]
            
        return await self._async(
            get_admin_realms_realm_events.asyncio, 
            realm,
            client_query=client,
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
        """Delete all user events (sync).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_events.sync_detailed,
            realm
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete events: {response.status_code}")

    async def adelete_events(self, realm: str | None = None) -> None:
        """Delete all user events (async).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_events.asyncio_detailed,
            realm
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
        date_from: Unset | str | datetime = UNSET,
        date_to: Unset | str | datetime = UNSET,
        direction: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        operation_types: Unset | list[str] | str = UNSET,
        resource_path: Unset | str = UNSET,
        resource_types: Unset | list[str] | str = UNSET,
    ) -> list[AdminEventRepresentation] | None:
        """Get admin events from the event store.
        
        Admin events track administrative actions performed in the realm.
        
        Args:
            realm: The realm name
            auth_client: Filter by authentication client
            auth_ip_address: Filter by authentication IP address
            auth_realm: Filter by authentication realm
            auth_user: Filter by authenticated user ID
            date_from: From date in ISO format
            date_to: To date in ISO format
            direction: Sort direction ("ASC" or "DESC")
            first: Pagination offset
            max: Maximum results to return
            operation_types: Operation type(s) to filter by - can be single string or list
            resource_path: Filter by resource path
            resource_types: Resource type(s) to filter by - can be single string or list
            
        Returns:
            List of admin events matching the filters
        """
        if isinstance(date_from, datetime) and date_from is not UNSET:
            date_from = date_from.isoformat()
        if isinstance(date_to, datetime) and date_to is not UNSET:
            date_to = date_to.isoformat()
        if isinstance(operation_types, str):
            operation_types = [operation_types]
        if isinstance(resource_types, str):
            resource_types = [resource_types]
            
        return self._sync(
            get_admin_realms_realm_admin_events.sync, 
            realm,
            auth_client=auth_client,
            auth_ip_address=auth_ip_address,
            auth_realm=auth_realm,
            auth_user=auth_user,
            date_from=date_from,
            date_to=date_to,
            direction=direction,
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
        date_from: Unset | str | datetime = UNSET,
        date_to: Unset | str | datetime = UNSET,
        direction: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        operation_types: Unset | list[str] | str = UNSET,
        resource_path: Unset | str = UNSET,
        resource_types: Unset | list[str] | str = UNSET,
    ) -> list[AdminEventRepresentation] | None:
        """Get admin events from the event store (async).
        
        Admin events track administrative actions performed in the realm.
        
        Args:
            realm: The realm name
            auth_client: Filter by authentication client
            auth_ip_address: Filter by authentication IP address
            auth_realm: Filter by authentication realm
            auth_user: Filter by authenticated user ID
            date_from: From date in ISO format
            date_to: To date in ISO format
            direction: Sort direction ("ASC" or "DESC")
            first: Pagination offset
            max: Maximum results to return
            operation_types: Operation type(s) to filter by - can be single string or list
            resource_path: Filter by resource path
            resource_types: Resource type(s) to filter by - can be single string or list
            
        Returns:
            List of admin events matching the filters
        """
        if isinstance(date_from, datetime):
            date_from = date_from.isoformat()
        if isinstance(date_to, datetime):
            date_to = date_to.isoformat()
        if isinstance(operation_types, str):
            operation_types = [operation_types]
        if isinstance(resource_types, str):
            resource_types = [resource_types]
            
        return await self._async(
            get_admin_realms_realm_admin_events.asyncio, 
            realm,
            auth_client=auth_client,
            auth_ip_address=auth_ip_address,
            auth_realm=auth_realm,
            auth_user=auth_user,
            date_from=date_from,
            date_to=date_to,
            direction=direction,
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
            APIError: If deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_admin_events.sync_detailed,
            realm
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete admin events: {response.status_code}")

    async def adelete_admin_events(self, realm: str | None = None) -> None:
        """Delete all admin events (async).
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_admin_events.asyncio_detailed,
            realm
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete admin events: {response.status_code}")

    def get_events_config(self, realm: str | None = None) -> RealmEventsConfigRepresentation | None:
        """Get events configuration (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            Event configuration for the realm
        """
        return self._sync(get_admin_realms_realm_events_config.sync, realm)

    async def aget_events_config(self, realm: str | None = None) -> RealmEventsConfigRepresentation | None:
        """Get events configuration (async).
        
        Args:
            realm: The realm name
            
        Returns:
            Event configuration for the realm
        """
        return await self._async(get_admin_realms_realm_events_config.asyncio, realm)

    def update_events_config(self, realm: str | None = None, *, config: dict | RealmEventsConfigRepresentation) -> None:
        """Update events configuration.
        
        Configures the event logging settings for the realm.
        
        Args:
            realm: The realm name
            config: Event configuration object or dict containing:
                - events_enabled: Enable user event logging
                - events_expiration: Event expiration time in seconds
                - events_listeners: List of event listener names
                - enabled_event_types: List of event types to log
                - admin_events_enabled: Enable admin event logging
                - admin_events_details_enabled: Include representation in admin events
                
        Raises:
            AuthError: If the update fails
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
        
        Configures the event logging settings for the realm.
        
        Args:
            realm: The realm name
            config: Event configuration object or dict containing:
                - events_enabled: Enable user event logging
                - events_expiration: Event expiration time in seconds
                - events_listeners: List of event listener names
                - enabled_event_types: List of event types to log
                - admin_events_enabled: Enable admin event logging
                - admin_events_details_enabled: Include representation in admin events
                
        Raises:
            AuthError: If the update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_events_config.asyncio_detailed,
            realm,
            config,
            RealmEventsConfigRepresentation
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update events config: {response.status_code}")


class EventsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the EventsAPI."""

    @cached_property
    def events(self) -> EventsAPI:
        """Get the EventsAPI instance.
        
        Returns:
            EventsAPI instance for managing events
        """
        return EventsAPI(manager=self)  # type: ignore[arg-type]
