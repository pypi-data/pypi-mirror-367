"""Session management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.realms_admin import (
    delete_admin_realms_realm_sessions_session,
    get_admin_realms_realm_client_session_stats,
)
from ..generated.api.clients import (
    get_admin_realms_realm_clients_client_uuid_session_count,
    get_admin_realms_realm_clients_client_uuid_user_sessions,
    get_admin_realms_realm_clients_client_uuid_offline_sessions,
    get_admin_realms_realm_clients_client_uuid_offline_session_count,
)
from ..generated.api.users import (
    get_admin_realms_realm_users_user_id_sessions,
    get_admin_realms_realm_users_user_id_offline_sessions_client_uuid,
)
from ..generated.models import UserSessionRepresentation
from ..generated.types import UNSET, Unset

__all__ = "SessionsAPI", "SessionsClientMixin", "UserSessionRepresentation"


class SessionsAPI(BaseAPI):
    """Session management API methods."""

    # Realm session operations
    def get_client_session_stats(self, realm: str | None = None) -> list[dict[str, str]] | None:
        """Get client session statistics for a realm (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of session statistics per client
        """
        return self._sync_ap_list(get_admin_realms_realm_client_session_stats.sync, realm)

    async def aget_client_session_stats(self, realm: str | None = None) -> list[dict[str, str]] | None:
        """Get client session statistics for a realm (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of session statistics per client
        """
        return await self._async_ap_list(get_admin_realms_realm_client_session_stats.asyncio, realm)

    def delete_session(self, realm: str | None = None, *, session: str, is_offline: Unset | bool = False) -> None:
        """Delete a session (sync).
        
        Args:
            realm: The realm name
            session: Session ID to delete
            is_offline: Whether this is an offline session
            
        Raises:
            APIError: If session deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_sessions_session.sync_detailed,
            realm,
            session=session,
            is_offline=is_offline
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete session: {response.status_code}")

    async def adelete_session(self, realm: str | None = None, *, session: str, is_offline: Unset | bool = False) -> None:
        """Delete a session (async).
        
        Args:
            realm: The realm name
            session: Session ID to delete
            is_offline: Whether this is an offline session
            
        Raises:
            APIError: If session deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_sessions_session.asyncio_detailed,
            realm,
            session=session,
            is_offline=is_offline
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete session: {response.status_code}")

    # Client session operations
    def get_client_session_count(self, realm: str | None = None, *, client_uuid: str) -> dict[str, int] | None:
        """Get session count for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Dictionary with session count information
        """
        return self._sync_ap(
            get_admin_realms_realm_clients_client_uuid_session_count.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_session_count(self, realm: str | None = None, *, client_uuid: str) -> dict[str, int] | None:
        """Get session count for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Dictionary with session count information
        """
        return await self._async_ap(
            get_admin_realms_realm_clients_client_uuid_session_count.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_client_user_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
    ) -> list[UserSessionRepresentation] | None:
        """Get user sessions for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of user sessions
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_user_sessions.sync,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    async def aget_client_user_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
    ) -> list[UserSessionRepresentation] | None:
        """Get user sessions for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of user sessions
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_user_sessions.asyncio,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    def get_client_offline_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
    ) -> list[UserSessionRepresentation] | None:
        """Get offline sessions for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of offline user sessions
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_offline_sessions.sync,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    async def aget_client_offline_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
    ) -> list[UserSessionRepresentation] | None:
        """Get offline sessions for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of offline user sessions
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_offline_sessions.asyncio,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    def get_client_offline_session_count(self, realm: str | None = None, *, client_uuid: str) -> dict[str, int] | None:
        """Get offline session count for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Dictionary with offline session count information
        """
        return self._sync_ap(
            get_admin_realms_realm_clients_client_uuid_offline_session_count.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_offline_session_count(self, realm: str | None = None, *, client_uuid: str) -> dict[str, int] | None:
        """Get offline session count for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Dictionary with offline session count information
        """
        return await self._async_ap(
            get_admin_realms_realm_clients_client_uuid_offline_session_count.asyncio,
            realm,
            client_uuid=client_uuid
        )

    # User session operations
    def get_user_sessions(self, realm: str | None = None, *, user_id: str) -> list[UserSessionRepresentation] | None:
        """Get sessions for a user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of active sessions for the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_sessions.sync,
            realm,
            user_id=user_id
        )

    async def aget_user_sessions(self, realm: str | None = None, *, user_id: str) -> list[UserSessionRepresentation] | None:
        """Get sessions for a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of active sessions for the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_sessions.asyncio,
            realm,
            user_id=user_id
        )

    def get_user_offline_sessions(self, realm: str | None = None, *, user_id: str, client_uuid: str) -> list[UserSessionRepresentation] | None:
        """Get offline sessions for a user and client (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_uuid: Client UUID
            
        Returns:
            List of offline sessions for the user with the specified client
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_offline_sessions_client_uuid.sync,
            realm,
            user_id=user_id,
            client_uuid=client_uuid
        )

    async def aget_user_offline_sessions(self, realm: str | None = None, *, user_id: str, client_uuid: str) -> list[UserSessionRepresentation] | None:
        """Get offline sessions for a user and client (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_uuid: Client UUID
            
        Returns:
            List of offline sessions for the user with the specified client
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_offline_sessions_client_uuid.asyncio,
            realm,
            user_id=user_id,
            client_uuid=client_uuid
        )


class SessionsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the SessionsAPI.
    """

    @cached_property
    def sessions(self) -> SessionsAPI:
        """Get the SessionsAPI instance."""
        return SessionsAPI(manager=self)  # type: ignore[arg-type]
