"""Client (application) management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.clients import (
    get_admin_realms_realm_clients,
    post_admin_realms_realm_clients,
    get_admin_realms_realm_clients_client_uuid,
    put_admin_realms_realm_clients_client_uuid,
    delete_admin_realms_realm_clients_client_uuid,
    get_admin_realms_realm_clients_client_uuid_client_secret,
    post_admin_realms_realm_clients_client_uuid_client_secret,
    get_admin_realms_realm_clients_client_uuid_service_account_user,
    get_admin_realms_realm_clients_client_uuid_session_count,
    get_admin_realms_realm_clients_client_uuid_offline_session_count,
    get_admin_realms_realm_clients_client_uuid_user_sessions,
    get_admin_realms_realm_clients_client_uuid_offline_sessions,
    get_admin_realms_realm_clients_client_uuid_default_client_scopes,
    put_admin_realms_realm_clients_client_uuid_default_client_scopes_client_scope_id,
    delete_admin_realms_realm_clients_client_uuid_default_client_scopes_client_scope_id,
    get_admin_realms_realm_clients_client_uuid_optional_client_scopes,
    put_admin_realms_realm_clients_client_uuid_optional_client_scopes_client_scope_id,
    delete_admin_realms_realm_clients_client_uuid_optional_client_scopes_client_scope_id,
    post_admin_realms_realm_clients_client_uuid_push_revocation,
    post_admin_realms_realm_clients_client_uuid_registration_access_token,
    get_admin_realms_realm_clients_client_uuid_management_permissions,
    put_admin_realms_realm_clients_client_uuid_management_permissions,
    post_admin_realms_realm_clients_client_uuid_nodes,
    delete_admin_realms_realm_clients_client_uuid_nodes_node,
    get_admin_realms_realm_clients_client_uuid_test_nodes_available,
)
from ..generated.models import (
    ClientRepresentation,
    ClientScopeRepresentation,
    CredentialRepresentation,
    GlobalRequestResult,
    ManagementPermissionReference,
    UserRepresentation,
    UserSessionRepresentation,
    PostAdminRealmsRealmClientsClientUuidNodesBody,
)
from ..generated.types import UNSET, Unset

__all__ = (
    "ClientsAPI",
    "ClientsClientMixin",
    "ClientRepresentation",
    "ClientScopeRepresentation",
    "ManagementPermissionReference",
    "GlobalRequestResult",
)


class ClientsAPI(BaseAPI):
    """Client (application) management API methods."""

    def get_all(
        self,
        realm: str | None = None,
        *,
        client_id: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        q: Unset | str = UNSET,
        search: Unset | bool = False,
        viewable_only: Unset | bool = False,
    ) -> list[ClientRepresentation] | None:
        """List clients in a realm.
        
        Args:
            realm: The realm name
            client_id: Filter by client ID (not UUID)
            first: Pagination offset
            max: Maximum results to return
            q: Query string for client search
            search: Boolean flag to enable searching
            viewable_only: Only return viewable clients
            
        Returns:
            List of clients matching the filters
        """
        return self._sync(
            get_admin_realms_realm_clients.sync,
            realm,
            client_id=client_id,
            first=first,
            max_=max,
            q=q,
            search=search,
            viewable_only=viewable_only,
        )

    async def aget_all(
        self,
        realm: str | None = None,
        *,
        client_id: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        q: Unset | str = UNSET,
        search: Unset | bool = False,
        viewable_only: Unset | bool = False,
    ) -> list[ClientRepresentation] | None:
        """List clients in a realm (async).
        
        Args:
            realm: The realm name
            client_id: Filter by client ID (not UUID)
            first: Pagination offset
            max: Maximum results to return
            q: Query string for client search
            search: Boolean flag to enable searching
            viewable_only: Only return viewable clients
            
        Returns:
            List of clients matching the filters
        """
        return await self._async(
            get_admin_realms_realm_clients.asyncio,
            realm,
            client_id=client_id,
            first=first,
            max_=max,
            q=q,
            search=search,
            viewable_only=viewable_only,
        )

    def create(self, realm: str | None = None, *, client_data: dict | ClientRepresentation) -> str:
        """Create a client (sync).
        
        Args:
            realm: The realm name
            client_data: Client configuration
            
        Returns:
            Created client UUID
            
        Raises:
            APIError: If client creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients.sync_detailed,
            realm,
            client_data,
            ClientRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def acreate(self, realm: str | None = None, *, client_data: dict | ClientRepresentation) -> str:
        """Create a client (async).
        
        Args:
            realm: The realm name
            client_data: Client configuration
            
        Returns:
            Created client UUID
            
        Raises:
            APIError: If client creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients.asyncio_detailed,
            realm,
            client_data,
            ClientRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def get(self, realm: str | None = None, *, client_uuid: str) -> ClientRepresentation | None:
        """Get a client by UUID (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Client representation with full details
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget(self, realm: str | None = None, *, client_uuid: str) -> ClientRepresentation | None:
        """Get a client by UUID (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Client representation with full details
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def update(self, realm: str | None = None, *, client_uuid: str, client_data: dict | ClientRepresentation) -> None:
        """Update a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID to update
            client_data: Updated client configuration
            
        Raises:
            APIError: If client update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid.sync_detailed,
            realm,
            client_data,
            ClientRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client: {response.status_code}")

    async def aupdate(self, realm: str | None = None, *, client_uuid: str, client_data: dict | ClientRepresentation) -> None:
        """Update a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID to update
            client_data: Updated client configuration
            
        Raises:
            APIError: If client update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid.asyncio_detailed,
            realm,
            client_data,
            ClientRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client: {response.status_code}")

    def delete(self, realm: str | None = None, *, client_uuid: str) -> None:
        """Delete a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID to delete
            
        Raises:
            APIError: If client deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid.sync_detailed,
            realm,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, client_uuid: str) -> None:
        """Delete a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID to delete
            
        Raises:
            APIError: If client deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid.asyncio_detailed,
            realm,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client: {response.status_code}")

    def get_secret(self, realm: str | None = None, *, client_uuid: str) -> CredentialRepresentation | None:
        """Get client secret (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Client secret credential
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_client_secret.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_secret(self, realm: str | None = None, *, client_uuid: str) -> CredentialRepresentation | None:
        """Get client secret (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Client secret credential
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_client_secret.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def regenerate_secret(self, realm: str | None = None, *, client_uuid: str) -> CredentialRepresentation | None:
        """Regenerate client secret (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            New client secret credential
        """
        return self._sync(
            post_admin_realms_realm_clients_client_uuid_client_secret.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aregenerate_secret(self, realm: str | None = None, *, client_uuid: str) -> CredentialRepresentation | None:
        """Regenerate client secret (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            New client secret credential
        """
        return await self._async(
            post_admin_realms_realm_clients_client_uuid_client_secret.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_service_account_user(self, realm: str | None = None, *, client_uuid: str) -> UserRepresentation | None:
        """Get service account user for client (sync).
        
        Service accounts are special users created for clients with service account enabled.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Service account user representation
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_service_account_user.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_service_account_user(self, realm: str | None = None, *, client_uuid: str) -> UserRepresentation | None:
        """Get service account user for client (async).
        
        Service accounts are special users created for clients with service account enabled.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Service account user representation
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_service_account_user.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_session_count(self, realm: str | None = None, *, client_uuid: str) -> int | None:
        """Get client session count (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Number of active sessions for the client
        """
        result = self._sync_ap(
            get_admin_realms_realm_clients_client_uuid_session_count.sync,
            realm,
            client_uuid=client_uuid
        )
        return result.get("count") if result else None

    async def aget_session_count(self, realm: str | None = None, *, client_uuid: str) -> int | None:
        """Get client session count (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Number of active sessions for the client
        """
        result = await self._async_ap(
            get_admin_realms_realm_clients_client_uuid_session_count.asyncio,
            realm,
            client_uuid=client_uuid
        )
        return result.get("count") if result else None

    def get_offline_session_count(self, realm: str | None = None, *, client_uuid: str) -> int | None:
        """Get client offline session count (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Number of offline sessions for the client
        """
        result = self._sync_ap(
            get_admin_realms_realm_clients_client_uuid_offline_session_count.sync,
            realm,
            client_uuid=client_uuid
        )
        return result.get("count") if result else None

    async def aget_offline_session_count(self, realm: str | None = None, *, client_uuid: str) -> int | None:
        """Get client offline session count (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Number of offline sessions for the client
        """
        result = await self._async_ap(
            get_admin_realms_realm_clients_client_uuid_offline_session_count.asyncio,
            realm,
            client_uuid=client_uuid
        )
        return result.get("count") if result else None

    def get_user_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: int | None = None,
        max: int | None = None
    ) -> list[UserSessionRepresentation] | None:
        """Get user sessions for client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of user sessions for the client
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_user_sessions.sync,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    async def aget_user_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: int | None = None,
        max: int | None = None
    ) -> list[UserSessionRepresentation] | None:
        """Get user sessions for client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of user sessions for the client
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_user_sessions.asyncio,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    def get_offline_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: int | None = None,
        max: int | None = None
    ) -> list[UserSessionRepresentation] | None:
        """Get offline sessions for client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of offline sessions for the client
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_offline_sessions.sync,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    async def aget_offline_sessions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: int | None = None,
        max: int | None = None
    ) -> list[UserSessionRepresentation] | None:
        """Get offline sessions for client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            
        Returns:
            List of offline sessions for the client
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_offline_sessions.asyncio,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
        )

    def get_default_client_scopes(self, realm: str | None = None, *, client_uuid: str) -> list[ClientScopeRepresentation] | None:
        """Get default client scopes (sync).
        
        Default scopes are always included in tokens.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of default client scopes
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_default_client_scopes.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_default_client_scopes(self, realm: str | None = None, *, client_uuid: str) -> list[ClientScopeRepresentation] | None:
        """Get default client scopes (async).
        
        Default scopes are always included in tokens.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of default client scopes
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_default_client_scopes.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def add_default_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Add default client scope (sync).
        
        Default scopes are always included in tokens.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to add as default
            
        Raises:
            APIError: If adding the scope fails
        """
        response = self._sync(
            put_admin_realms_realm_clients_client_uuid_default_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add default client scope: {response.status_code}")

    async def aadd_default_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Add default client scope (async).
        
        Default scopes are always included in tokens.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to add as default
            
        Raises:
            APIError: If adding the scope fails
        """
        response = await self._async(
            put_admin_realms_realm_clients_client_uuid_default_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add default client scope: {response.status_code}")

    def remove_default_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Remove default client scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to remove from defaults
            
        Raises:
            APIError: If removing the scope fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_default_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove default client scope: {response.status_code}")

    async def aremove_default_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Remove default client scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to remove from defaults
            
        Raises:
            APIError: If removing the scope fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_default_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove default client scope: {response.status_code}")

    def get_optional_client_scopes(self, realm: str | None = None, *, client_uuid: str) -> list[ClientScopeRepresentation] | None:
        """Get optional client scopes (sync).
        
        Optional scopes must be explicitly requested in authorization requests.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of optional client scopes
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_optional_client_scopes.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_optional_client_scopes(self, realm: str | None = None, *, client_uuid: str) -> list[ClientScopeRepresentation] | None:
        """Get optional client scopes (async).
        
        Optional scopes must be explicitly requested in authorization requests.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of optional client scopes
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_optional_client_scopes.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def add_optional_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Add optional client scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to add as optional
            
        Raises:
            APIError: If adding the scope fails
        """
        response = self._sync(
            put_admin_realms_realm_clients_client_uuid_optional_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add optional client scope: {response.status_code}")

    async def aadd_optional_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Add optional client scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to add as optional
            
        Raises:
            APIError: If adding the scope fails
        """
        response = await self._async(
            put_admin_realms_realm_clients_client_uuid_optional_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add optional client scope: {response.status_code}")

    def remove_optional_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Remove optional client scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to remove from optionals
            
        Raises:
            APIError: If removing the scope fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_optional_client_scopes_client_scope_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove optional client scope: {response.status_code}")

    async def aremove_optional_client_scope(self, realm: str | None = None, *, client_uuid: str, client_scope_id: str) -> None:
        """Remove optional client scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            client_scope_id: Client scope ID to remove from optionals
            
        Raises:
            APIError: If removing the scope fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_optional_client_scopes_client_scope_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove optional client scope: {response.status_code}")

    def push_revocation(self, realm: str | None = None, *, client_uuid: str) -> None:
        """Push revocation policy to client (sync).
        
        Notifies the client adapter to revoke any cached sessions.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Raises:
            APIError: If push revocation fails
        """
        response = self._sync(
            post_admin_realms_realm_clients_client_uuid_push_revocation.sync_detailed,
            realm,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to push revocation: {response.status_code}")

    async def apush_revocation(self, realm: str | None = None, *, client_uuid: str) -> None:
        """Push revocation policy to client (async).
        
        Notifies the client adapter to revoke any cached sessions.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Raises:
            APIError: If push revocation fails
        """
        response = await self._async(
            post_admin_realms_realm_clients_client_uuid_push_revocation.asyncio_detailed,
            realm,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to push revocation: {response.status_code}")

    def regenerate_registration_token(self, realm: str | None = None, *, client_uuid: str) -> ClientRepresentation | None:
        """Regenerate registration access token (sync).
        
        Creates a new registration access token for dynamic client registration.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Registration access token details
        """
        return self._sync(
            post_admin_realms_realm_clients_client_uuid_registration_access_token.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aregenerate_registration_token(self, realm: str | None = None, *, client_uuid: str) -> ClientRepresentation | None:
        """Regenerate registration access token (async).
        
        Creates a new registration access token for dynamic client registration.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Registration access token details
        """
        return await self._async(
            post_admin_realms_realm_clients_client_uuid_registration_access_token.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def get_management_permissions(self, realm: str | None = None, *, client_uuid: str) -> ManagementPermissionReference | None:
        """Get management permissions for client (sync).
        
        Returns whether client authorization permissions have been initialized.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Management permission reference
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_management_permissions.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_management_permissions(self, realm: str | None = None, *, client_uuid: str) -> ManagementPermissionReference | None:
        """Get management permissions for client (async).
        
        Returns whether client authorization permissions have been initialized.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Management permission reference
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_management_permissions.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def update_management_permissions(self, realm: str | None = None, *, client_uuid: str, permissions: dict | ManagementPermissionReference) -> ManagementPermissionReference | None:
        """Update management permissions for client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            permissions: Management permissions to set
            
        Returns:
            Updated management permission reference
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid_management_permissions.sync_detailed,
            realm,
            permissions,
            ManagementPermissionReference,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update management permissions: {response.status_code}")
        return response.parsed

    async def aupdate_management_permissions(self, realm: str | None = None, *, client_uuid: str, permissions: dict | ManagementPermissionReference) -> ManagementPermissionReference | None:
        """Update management permissions for client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            permissions: Management permissions to set
            
        Returns:
            Updated management permission reference
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid_management_permissions.asyncio_detailed,
            realm,
            permissions,
            ManagementPermissionReference,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update management permissions: {response.status_code}")
        return response.parsed

    def register_node(self, realm: str | None = None, *, client_uuid: str, node_data: dict | PostAdminRealmsRealmClientsClientUuidNodesBody) -> None:
        """Register a cluster node with the client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            node_data: Node registration data
            
        Raises:
            APIError: If node registration fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_nodes.sync_detailed,
            realm,
            node_data,
            PostAdminRealmsRealmClientsClientUuidNodesBody,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to register node: {response.status_code}")

    async def aregister_node(self, realm: str | None = None, *, client_uuid: str, node_data: dict | PostAdminRealmsRealmClientsClientUuidNodesBody) -> None:
        """Register a cluster node with the client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            node_data: Node registration data
            
        Raises:
            APIError: If node registration fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_nodes.asyncio_detailed,
            realm,
            node_data,
            PostAdminRealmsRealmClientsClientUuidNodesBody,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to register node: {response.status_code}")

    def unregister_node(self, realm: str | None = None, *, client_uuid: str, node: str) -> None:
        """Unregister a cluster node from the client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            node: Node name to unregister
            
        Raises:
            APIError: If node unregistration fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_nodes_node.sync_detailed,
            realm,
            client_uuid=client_uuid,
            node=node
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to unregister node: {response.status_code}")

    async def aunregister_node(self, realm: str | None = None, *, client_uuid: str, node: str) -> None:
        """Unregister a cluster node from the client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            node: Node name to unregister
            
        Raises:
            APIError: If node unregistration fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_nodes_node.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            node=node
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to unregister node: {response.status_code}")

    def test_nodes_available(self, realm: str | None = None, *, client_uuid: str) -> GlobalRequestResult | None:
        """Test if registered cluster nodes are available (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Node availability test results
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_test_nodes_available.sync,
            realm,
            client_uuid=client_uuid
        )

    async def atest_nodes_available(self, realm: str | None = None, *, client_uuid: str) -> GlobalRequestResult | None:
        """Test if registered cluster nodes are available (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Node availability test results
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_test_nodes_available.asyncio,
            realm,
            client_uuid=client_uuid
        )


class ClientsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ClientsAPI."""

    @cached_property
    def clients(self) -> ClientsAPI:
        """Get the ClientsAPI instance.
        
        Returns:
            ClientsAPI instance for managing clients
        """
        return ClientsAPI(manager=self)  # type: ignore[arg-type]
