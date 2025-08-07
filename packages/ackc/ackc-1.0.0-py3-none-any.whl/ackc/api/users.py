"""User management API methods."""
from functools import cached_property
from typing import Any

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.users import (
    get_admin_realms_realm_users,
    get_admin_realms_realm_users_count,
    post_admin_realms_realm_users,
    get_admin_realms_realm_users_user_id,
    put_admin_realms_realm_users_user_id,
    delete_admin_realms_realm_users_user_id,
    get_admin_realms_realm_users_user_id_groups,
    get_admin_realms_realm_users_user_id_groups_count,
    put_admin_realms_realm_users_user_id_groups_group_id,
    delete_admin_realms_realm_users_user_id_groups_group_id,
    put_admin_realms_realm_users_user_id_reset_password,
    put_admin_realms_realm_users_user_id_send_verify_email,
    get_admin_realms_realm_users_user_id_sessions,
    post_admin_realms_realm_users_user_id_logout,
    get_admin_realms_realm_users_user_id_credentials,
    delete_admin_realms_realm_users_user_id_credentials_credential_id,
    get_admin_realms_realm_users_user_id_consents,
    delete_admin_realms_realm_users_user_id_consents_client,
    get_admin_realms_realm_users_user_id_federated_identity,
    post_admin_realms_realm_users_user_id_federated_identity_provider,
    delete_admin_realms_realm_users_user_id_federated_identity_provider,
    post_admin_realms_realm_users_user_id_impersonation,
    get_admin_realms_realm_users_user_id_offline_sessions_client_uuid,
    put_admin_realms_realm_users_user_id_execute_actions_email,
    get_admin_realms_realm_users_profile,
    put_admin_realms_realm_users_profile,
    get_admin_realms_realm_users_profile_metadata,
    get_admin_realms_realm_users_user_id_configured_user_storage_credential_types,
    get_admin_realms_realm_users_user_id_unmanaged_attributes,
    post_admin_realms_realm_users_user_id_credentials_credential_id_move_after_new_previous_credential_id,
    post_admin_realms_realm_users_user_id_credentials_credential_id_move_to_first,
    put_admin_realms_realm_users_user_id_disable_credential_types,
    put_admin_realms_realm_users_user_id_reset_password_email,
)
from ..generated.models import (
    UserRepresentation,
    GroupRepresentation,
    CredentialRepresentation,
    UserSessionRepresentation,
    UserConsentRepresentation,
    FederatedIdentityRepresentation,
    UPConfig,
    UserProfileMetadata,
)
from ..generated.types import UNSET, Unset

__all__ = (
    "UsersAPI",
    "UsersClientMixin",
    "UserRepresentation",
    "GroupRepresentation",
    "CredentialRepresentation",
    "UserSessionRepresentation",
    "UserConsentRepresentation",
    "FederatedIdentityRepresentation",
)


class UsersAPI(BaseAPI):
    """User management API methods."""

    def get_all(
        self,
        realm: str | None = None,
        *,
        brief_representation: Unset | bool = UNSET,
        email: Unset | str = UNSET,
        email_verified: Unset | bool = UNSET,
        enabled: Unset | bool = UNSET,
        exact: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        first_name: Unset | str = UNSET,
        idp_alias: Unset | str = UNSET,
        idp_user_id: Unset | str = UNSET,
        last_name: Unset | str = UNSET,
        max: Unset | int = UNSET,
        q: Unset | str = UNSET,
        search: Unset | str = UNSET,
        username: Unset | str = UNSET,
    ) -> list[UserRepresentation] | None:
        """List users in a realm.
        
        Args:
            realm: The realm name
            brief_representation: Only return basic user info (default True)
            email: Filter by email address
            email_verified: Filter by verified email status
            enabled: Filter by enabled status
            exact: Exact match for username/email searches
            first: Pagination offset
            first_name: Filter by first name
            idp_alias: Filter by identity provider alias
            idp_user_id: Filter by identity provider user ID
            last_name: Filter by last name
            max: Maximum results to return (default 100)
            q: General query string for user search
            search: Search string (searches username, first/last name, email)
            username: Filter by username
            
        Returns:
            List of users matching the filters
        """
        return self._sync(
            get_admin_realms_realm_users.sync,
            realm,
            brief_representation=brief_representation,
            email=email,
            email_verified=email_verified,
            enabled=enabled,
            exact=exact,
            first=first,
            first_name=first_name,
            idp_alias=idp_alias,
            idp_user_id=idp_user_id,
            last_name=last_name,
            max_=max,
            q=q,
            search=search,
            username=username,
        )
    
    async def aget_all(
        self,
        realm: str | None = None,
        *,
        brief_representation: Unset | bool = UNSET,
        email: Unset | str = UNSET,
        email_verified: Unset | bool = UNSET,
        enabled: Unset | bool = UNSET,
        exact: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        first_name: Unset | str = UNSET,
        idp_alias: Unset | str = UNSET,
        idp_user_id: Unset | str = UNSET,
        last_name: Unset | str = UNSET,
        max: Unset | int = UNSET,
        q: Unset | str = UNSET,
        search: Unset | str = UNSET,
        username: Unset | str = UNSET,
    ) -> list[UserRepresentation] | None:
        """List users in a realm (async).
        
        Args:
            realm: The realm name
            brief_representation: Only return basic user info (default True)
            email: Filter by email address
            email_verified: Filter by verified email status
            enabled: Filter by enabled status
            exact: Exact match for username/email searches
            first: Pagination offset
            first_name: Filter by first name
            idp_alias: Filter by identity provider alias
            idp_user_id: Filter by identity provider user ID
            last_name: Filter by last name
            max: Maximum results to return (default 100)
            q: General query string for user search
            search: Search string (searches username, first/last name, email)
            username: Filter by username
            
        Returns:
            List of users matching the filters
        """
        return await self._async(
            get_admin_realms_realm_users.asyncio,
            realm,
            brief_representation=brief_representation,
            email=email,
            email_verified=email_verified,
            enabled=enabled,
            exact=exact,
            first=first,
            first_name=first_name,
            idp_alias=idp_alias,
            idp_user_id=idp_user_id,
            last_name=last_name,
            max_=max,
            q=q,
            search=search,
            username=username,
        )
    
    def create(self, realm: str | None = None, *, user_data: dict | UserRepresentation) -> str:
        """Create a user (sync).
        
        Args:
            realm: The realm name
            user_data: User configuration including username, email, etc.
            
        Returns:
            Created user's ID
            
        Raises:
            APIError: If user creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_users.sync_detailed,
            realm,
            user_data,
            UserRepresentation
        )

        if response.status_code != 201:
            raise APIError(f"Failed to create user: {response.status_code}")

        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""
    
    async def acreate(self, realm: str | None = None, *, user_data: dict | UserRepresentation) -> str:
        """Create a user (async).
        
        Args:
            realm: The realm name
            user_data: User configuration including username, email, etc.
            
        Returns:
            Created user's ID
            
        Raises:
            APIError: If user creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_users.asyncio_detailed,
            realm,
            user_data,
            UserRepresentation
        )

        if response.status_code != 201:
            raise APIError(f"Failed to create user: {response.status_code}")

        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""
    
    def get(self, realm: str | None = None, *, user_id: str) -> UserRepresentation | None:
        """Get a user by ID (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            User representation with full details
        """
        return self._sync(get_admin_realms_realm_users_user_id.sync, realm=realm, user_id=user_id)
    
    async def aget(self, realm: str | None = None, *, user_id: str) -> UserRepresentation | None:
        """Get a user by ID (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            User representation with full details
        """
        return await self._async(get_admin_realms_realm_users_user_id.asyncio, realm=realm, user_id=user_id)

    def update(self, realm: str | None = None, *, user_id: str, user_data: dict | UserRepresentation) -> None:
        """Update a user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID to update
            user_data: Updated user configuration
            
        Raises:
            APIError: If user update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_users_user_id.sync_detailed,
            realm,
            user_data,
            UserRepresentation,
            user_id=user_id
        )

        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update user: {response.status_code}")
    
    async def aupdate(self, realm: str | None = None, *, user_id: str, user_data: dict | UserRepresentation) -> None:
        """Update a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID to update
            user_data: Updated user configuration
            
        Raises:
            APIError: If user update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_users_user_id.asyncio_detailed,
            realm,
            user_data,
            UserRepresentation,
            user_id=user_id
        )

        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update user: {response.status_code}")

    def delete(self, realm: str | None = None, *, user_id: str) -> None:
        """Delete a user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID to delete
            
        Raises:
            APIError: If user deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_users_user_id.sync_detailed,
            realm,
            user_id=user_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete user: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, user_id: str) -> None:
        """Delete a user (async).
        
        Args:
            realm: The realm name
            user_id: User ID to delete
            
        Raises:
            APIError: If user deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_users_user_id.asyncio_detailed,
            realm,
            user_id=user_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete user: {response.status_code}")

    def get_count(
        self,
        realm: str | None = None,
        *,
        email: Unset | str = UNSET,
        email_verified: Unset | bool = UNSET,
        enabled: Unset | bool = UNSET,
        first_name: Unset | str = UNSET,
        last_name: Unset | str = UNSET,
        q: Unset | str = UNSET,
        search: Unset | str = UNSET,
        username: Unset | str = UNSET,
    ) -> int:
        """Get total user count (sync).
        
        Args:
            realm: The realm name
            email: Filter by email address
            email_verified: Filter by verified email status
            enabled: Filter by enabled status
            first_name: Filter by first name
            last_name: Filter by last name
            q: General query string for user search
            search: Search string (searches username, first/last name, email)
            username: Filter by username
            
        Returns:
            Total number of users matching the filters
        """
        return self._sync(
            get_admin_realms_realm_users_count.sync,
            realm,
            email=email,
            email_verified=email_verified,
            enabled=enabled,
            first_name=first_name,
            last_name=last_name,
            q=q,
            search=search,
            username=username,
        )

    async def aget_count(
        self,
        realm: str | None = None,
        *,
        email: Unset | str = UNSET,
        email_verified: Unset | bool = UNSET,
        enabled: Unset | bool = UNSET,
        first_name: Unset | str = UNSET,
        last_name: Unset | str = UNSET,
        q: Unset | str = UNSET,
        search: Unset | str = UNSET,
        username: Unset | str = UNSET,
    ) -> int:
        """Get total user count (async).
        
        Args:
            realm: The realm name
            email: Filter by email address
            email_verified: Filter by verified email status
            enabled: Filter by enabled status
            first_name: Filter by first name
            last_name: Filter by last name
            q: General query string for user search
            search: Search string (searches username, first/last name, email)
            username: Filter by username
            
        Returns:
            Total number of users matching the filters
        """
        return await self._async(
            get_admin_realms_realm_users_count.asyncio,
            realm,
            email=email,
            email_verified=email_verified,
            enabled=enabled,
            first_name=first_name,
            last_name=last_name,
            q=q,
            search=search,
            username=username,
        )

    def get_groups(self, realm: str | None = None, *, user_id: str) -> list[GroupRepresentation] | None:
        """Get user's group memberships (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of groups the user belongs to
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_groups.sync,
            realm,
            user_id=user_id,
        )

    async def aget_groups(self, realm: str | None = None, *, user_id: str) -> list[GroupRepresentation] | None:
        """Get user's group memberships (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of groups the user belongs to
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_groups.asyncio,
            realm,
            user_id=user_id,
        )

    def add_to_group(self, realm: str | None = None, *, user_id: str, group_id: str) -> None:
        """Add user to group (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            group_id: Group ID to add user to
            
        Raises:
            APIError: If adding user to group fails
        """
        response = self._sync(
            put_admin_realms_realm_users_user_id_groups_group_id.sync_detailed,
            realm,
            user_id=user_id,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add user to group: {response.status_code}")

    async def aadd_to_group(self, realm: str | None = None, *, user_id: str, group_id: str) -> None:
        """Add user to group (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            group_id: Group ID to add user to
            
        Raises:
            APIError: If adding user to group fails
        """
        response = await self._async(
            put_admin_realms_realm_users_user_id_groups_group_id.asyncio_detailed,
            realm,
            user_id=user_id,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add user to group: {response.status_code}")

    def remove_from_group(self, realm: str | None = None, *, user_id: str, group_id: str) -> None:
        """Remove user from group (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            group_id: Group ID to remove user from
            
        Raises:
            APIError: If removing user from group fails
        """
        response = self._sync(
            delete_admin_realms_realm_users_user_id_groups_group_id.sync_detailed,
            realm,
            user_id=user_id,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove user from group: {response.status_code}")

    async def aremove_from_group(self, realm: str | None = None, *, user_id: str, group_id: str) -> None:
        """Remove user from group (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            group_id: Group ID to remove user from
            
        Raises:
            APIError: If removing user from group fails
        """
        response = await self._async(
            delete_admin_realms_realm_users_user_id_groups_group_id.asyncio_detailed,
            realm,
            user_id=user_id,
            group_id=group_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove user from group: {response.status_code}")

    def reset_password(self, realm: str | None = None, *, user_id: str, password: str, temporary: bool = False) -> None:
        """Reset user password (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            password: New password
            temporary: Whether password is temporary and must be changed on next login
            
        Raises:
            APIError: If password reset fails
        """
        credential = CredentialRepresentation(
            type_="password",
            value=password,
            temporary=temporary,
        )
        response = self._sync_detailed(
            put_admin_realms_realm_users_user_id_reset_password.sync_detailed,
            realm,
            user_id=user_id,
            body=credential,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to reset password: {response.status_code}")

    async def areset_password(self, realm: str | None = None, *, user_id: str, password: str, temporary: bool = False) -> None:
        """Reset user password (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            password: New password
            temporary: Whether password is temporary and must be changed on next login
            
        Raises:
            APIError: If password reset fails
        """
        credential = CredentialRepresentation(
            type_="password",
            value=password,
            temporary=temporary,
        )
        response = await self._async_detailed(
            put_admin_realms_realm_users_user_id_reset_password.asyncio_detailed,
            realm,
            user_id=user_id,
            body=credential,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to reset password: {response.status_code}")

    def send_verify_email(self, realm: str | None = None, *, user_id: str, redirect_uri: Unset | str = UNSET) -> None:
        """Send email verification (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            redirect_uri: URL to redirect to after email verification
            
        Raises:
            APIError: If sending verification email fails
        """
        response = self._sync(
            put_admin_realms_realm_users_user_id_send_verify_email.sync_detailed,
            realm,
            user_id=user_id,
            redirect_uri=redirect_uri
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to send verification email: {response.status_code}")

    async def asend_verify_email(self, realm: str | None = None, *, user_id: str, redirect_uri: Unset | str = UNSET) -> None:
        """Send email verification (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            redirect_uri: URL to redirect to after email verification
            
        Raises:
            APIError: If sending verification email fails
        """
        response = await self._async(
            put_admin_realms_realm_users_user_id_send_verify_email.asyncio_detailed,
            realm,
            user_id=user_id,
            redirect_uri=redirect_uri
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to send verification email: {response.status_code}")

    def get_sessions(self, realm: str | None = None, *, user_id: str) -> list[UserSessionRepresentation] | None:
        """Get user's active sessions (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of user's active sessions
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_sessions.sync,
            realm,
            user_id=user_id,
        )

    async def aget_sessions(self, realm: str | None = None, *, user_id: str) -> list[UserSessionRepresentation] | None:
        """Get user's active sessions (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of user's active sessions
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_sessions.asyncio,
            realm,
            user_id=user_id,
        )

    def logout(self, realm: str | None = None, *, user_id: str) -> None:
        """Force logout user from all sessions (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Raises:
            APIError: If logout operation fails
        """
        response = self._sync(
            post_admin_realms_realm_users_user_id_logout.sync_detailed,
            realm,
            user_id=user_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to logout user: {response.status_code}")

    async def alogout(self, realm: str | None = None, *, user_id: str) -> None:
        """Force logout user from all sessions (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Raises:
            APIError: If logout operation fails
        """
        response = await self._async(
            post_admin_realms_realm_users_user_id_logout.asyncio_detailed,
            realm,
            user_id=user_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to logout user: {response.status_code}")

    def get_credentials(self, realm: str | None = None, *, user_id: str) -> list[CredentialRepresentation] | None:
        """Get user's credentials (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of user's credentials
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_credentials.sync,
            realm,
            user_id=user_id,
        )

    async def aget_credentials(self, realm: str | None = None, *, user_id: str) -> list[CredentialRepresentation] | None:
        """Get user's credentials (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of user's credentials
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_credentials.asyncio,
            realm,
            user_id=user_id,
        )

    def delete_credential(self, realm: str | None = None, *, user_id: str, credential_id: str) -> None:
        """Delete specific credential (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_id: Credential ID to delete
            
        Raises:
            APIError: If credential deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_users_user_id_credentials_credential_id.sync_detailed,
            realm,
            user_id=user_id,
            credential_id=credential_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete credential: {response.status_code}")

    async def adelete_credential(self, realm: str | None = None, *, user_id: str, credential_id: str) -> None:
        """Delete specific credential (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_id: Credential ID to delete
            
        Raises:
            APIError: If credential deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_users_user_id_credentials_credential_id.asyncio_detailed,
            realm,
            user_id=user_id,
            credential_id=credential_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete credential: {response.status_code}")

    def get_groups_count(self, realm: str | None = None, *, user_id: str) -> int | None:
        """Get count of user's group memberships (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            Number of groups the user belongs to
        """
        result = self._sync_ap(
            get_admin_realms_realm_users_user_id_groups_count.sync,
            realm,
            user_id=user_id,
        )
        return result.get("count") if result else None

    async def aget_groups_count(self, realm: str | None = None, *, user_id: str) -> int | None:
        """Get count of user's group memberships (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            Number of groups the user belongs to
        """
        result = await self._async_ap(
            get_admin_realms_realm_users_user_id_groups_count.asyncio,
            realm,
            user_id=user_id,
        )
        return result.get("count") if result else None

    def get_consents(self, realm: str | None = None, *, user_id: str) -> list[UserConsentRepresentation] | None:
        """Get user's consents (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of user's consents for clients
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_consents.sync,
            realm,
            user_id=user_id,
        )

    async def aget_consents(self, realm: str | None = None, *, user_id: str) -> list[UserConsentRepresentation] | None:
        """Get user's consents (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of user's consents for clients
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_consents.asyncio,
            realm,
            user_id=user_id,
        )

    def revoke_consent(self, realm: str | None = None, *, user_id: str, client_path: str) -> None:
        """Revoke user consent for client (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_path: Client ID to revoke consent for
            
        Raises:
            APIError: If revoking consent fails
        """
        response = self._sync(
            delete_admin_realms_realm_users_user_id_consents_client.sync_detailed,
            realm,
            user_id=user_id,
            client_path=client_path
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to revoke consent: {response.status_code}")

    async def arevoke_consent(self, realm: str | None = None, *, user_id: str, client_path: str) -> None:
        """Revoke user consent for client (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_path: Client ID to revoke consent for
            
        Raises:
            APIError: If revoking consent fails
        """
        response = await self._async(
            delete_admin_realms_realm_users_user_id_consents_client.asyncio_detailed,
            realm,
            user_id=user_id,
            client_path=client_path
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to revoke consent: {response.status_code}")

    def get_federated_identities(self, realm: str | None = None, *, user_id: str) -> list[FederatedIdentityRepresentation] | None:
        """Get user's federated identities (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of federated identities linked to the user
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_federated_identity.sync,
            realm,
            user_id=user_id,
        )

    async def aget_federated_identities(self, realm: str | None = None, *, user_id: str) -> list[FederatedIdentityRepresentation] | None:
        """Get user's federated identities (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of federated identities linked to the user
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_federated_identity.asyncio,
            realm,
            user_id=user_id,
        )

    def add_federated_identity(self, realm: str | None = None, *, user_id: str, provider: str, rep: dict | FederatedIdentityRepresentation) -> None:
        """Add federated identity to user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            provider: Identity provider alias
            rep: Federated identity representation
            
        Raises:
            APIError: If adding federated identity fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_users_user_id_federated_identity_provider.sync_detailed,
            realm,
            rep,
            FederatedIdentityRepresentation,
            user_id=user_id,
            provider=provider
        )
        if response.status_code not in (200, 201, 204):
            raise APIError(f"Failed to add federated identity: {response.status_code}")

    async def aadd_federated_identity(self, realm: str | None = None, *, user_id: str, provider: str, rep: dict | FederatedIdentityRepresentation) -> None:
        """Add federated identity to user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            provider: Identity provider alias
            rep: Federated identity representation
            
        Raises:
            APIError: If adding federated identity fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_users_user_id_federated_identity_provider.asyncio_detailed,
            realm,
            rep,
            FederatedIdentityRepresentation,
            user_id=user_id,
            provider=provider
        )
        if response.status_code not in (200, 201, 204):
            raise APIError(f"Failed to add federated identity: {response.status_code}")

    def remove_federated_identity(self, realm: str | None = None, *, user_id: str, provider: str) -> None:
        """Remove federated identity from user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            provider: Identity provider alias to remove
            
        Raises:
            APIError: If removing federated identity fails
        """
        response = self._sync(
            delete_admin_realms_realm_users_user_id_federated_identity_provider.sync_detailed,
            realm,
            user_id=user_id,
            provider=provider
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove federated identity: {response.status_code}")

    async def aremove_federated_identity(self, realm: str | None = None, *, user_id: str, provider: str) -> None:
        """Remove federated identity from user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            provider: Identity provider alias to remove
            
        Raises:
            APIError: If removing federated identity fails
        """
        response = await self._async(
            delete_admin_realms_realm_users_user_id_federated_identity_provider.asyncio_detailed,
            realm,
            user_id=user_id,
            provider=provider
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to remove federated identity: {response.status_code}")

    def impersonate(self, realm: str | None = None, *, user_id: str) -> dict[str, Any] | None:
        """Impersonate user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID to impersonate
            
        Returns:
            Impersonation session details
        """
        return self._sync_ap(
            post_admin_realms_realm_users_user_id_impersonation.sync,
            realm,
            user_id=user_id,
        )

    async def aimpersonate(self, realm: str | None = None, *, user_id: str) -> dict[str, Any] | None:
        """Impersonate user (async).
        
        Args:
            realm: The realm name
            user_id: User ID to impersonate
            
        Returns:
            Impersonation session details
        """
        return await self._async_ap(
            post_admin_realms_realm_users_user_id_impersonation.asyncio,
            realm,
            user_id=user_id,
        )

    def get_offline_sessions(self, realm: str | None = None, *, user_id: str, client_uuid: str) -> list[UserSessionRepresentation] | None:
        """Get user's offline sessions for a client (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_uuid: Client UUID
            
        Returns:
            List of offline sessions for the client
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_offline_sessions_client_uuid.sync,
            realm,
            user_id=user_id,
            client_uuid=client_uuid,
        )

    async def aget_offline_sessions(self, realm: str | None = None, *, user_id: str, client_uuid: str) -> list[UserSessionRepresentation] | None:
        """Get user's offline sessions for a client (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            client_uuid: Client UUID
            
        Returns:
            List of offline sessions for the client
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_offline_sessions_client_uuid.asyncio,
            realm,
            user_id=user_id,
            client_uuid=client_uuid,
        )

    def execute_actions_email(self, realm: str | None = None, *, user_id: str, actions: list[str], redirect_uri: str | None = None, client_id: str | None = None, lifespan: int | None = None) -> None:
        """Send execute actions email to user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            actions: List of required actions to execute
            redirect_uri: URL to redirect to after actions are completed
            client_id: Client ID initiating the action
            lifespan: Email link lifespan in seconds
            
        Raises:
            APIError: If sending execute actions email fails
        """
        response = self._sync_detailed(
            put_admin_realms_realm_users_user_id_execute_actions_email.sync_detailed,
            realm,
            user_id=user_id,
            body=actions,
            redirect_uri=redirect_uri,
            client_id=client_id,
            lifespan=lifespan,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to send execute actions email: {response.status_code}")

    async def aexecute_actions_email(self, realm: str | None = None, *, user_id: str, actions: list[str], redirect_uri: str | None = None, client_id: str | None = None, lifespan: int | None = None) -> None:
        """Send execute actions email to user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            actions: List of required actions to execute
            redirect_uri: URL to redirect to after actions are completed
            client_id: Client ID initiating the action
            lifespan: Email link lifespan in seconds
            
        Raises:
            APIError: If sending execute actions email fails
        """
        response = await self._async_detailed(
            put_admin_realms_realm_users_user_id_execute_actions_email.asyncio_detailed,
            realm,
            user_id=user_id,
            body=actions,
            redirect_uri=redirect_uri,
            client_id=client_id,
            lifespan=lifespan,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to send execute actions email: {response.status_code}")

    def get_configured_credential_types(self, realm: str | None = None, *, user_id: str) -> list[str] | None:
        """Get configured user storage credential types (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of configured credential types
        """
        return self._sync(
            get_admin_realms_realm_users_user_id_configured_user_storage_credential_types.sync,
            realm,
            user_id=user_id,
        )

    async def aget_configured_credential_types(self, realm: str | None = None, *, user_id: str) -> list[str] | None:
        """Get configured user storage credential types (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            List of configured credential types
        """
        return await self._async(
            get_admin_realms_realm_users_user_id_configured_user_storage_credential_types.asyncio,
            realm,
            user_id=user_id,
        )

    def get_unmanaged_attributes(self, realm: str | None = None, *, user_id: str) -> dict[str, list[str]] | None:
        """Get unmanaged attributes (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            Dictionary of unmanaged user attributes
        """
        return self._sync_ap(
            get_admin_realms_realm_users_user_id_unmanaged_attributes.sync,
            realm,
            user_id=user_id,
        )

    async def aget_unmanaged_attributes(self, realm: str | None = None, *, user_id: str) -> dict[str, list[str]] | None:
        """Get unmanaged attributes (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            
        Returns:
            Dictionary of unmanaged user attributes
        """
        return await self._async_ap(
            get_admin_realms_realm_users_user_id_unmanaged_attributes.asyncio,
            realm,
            user_id=user_id,
        )

    def move_credential_after(
        self,
        realm: str | None = None,
        *,
        user_id: str,
        credential_id: str,
        new_previous_credential_id: str
    ) -> None:
        """Move credential after another credential (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_id: Credential ID to move
            new_previous_credential_id: Credential ID to move after
            
        Raises:
            APIError: If moving credential fails
        """
        response = self._sync(
            post_admin_realms_realm_users_user_id_credentials_credential_id_move_after_new_previous_credential_id.sync_detailed,
            realm,
            user_id=user_id,
            credential_id=credential_id,
            new_previous_credential_id=new_previous_credential_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to move credential: {response.status_code}")

    async def amove_credential_after(
        self,
        realm: str | None = None,
        *,
        user_id: str,
        credential_id: str,
        new_previous_credential_id: str
    ) -> None:
        """Move credential after another credential (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_id: Credential ID to move
            new_previous_credential_id: Credential ID to move after
            
        Raises:
            APIError: If moving credential fails
        """
        response = await self._async(
            post_admin_realms_realm_users_user_id_credentials_credential_id_move_after_new_previous_credential_id.asyncio_detailed,
            realm,
            user_id=user_id,
            credential_id=credential_id,
            new_previous_credential_id=new_previous_credential_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to move credential: {response.status_code}")

    def move_credential_to_first(self, realm: str | None = None, *, user_id: str, credential_id: str) -> None:
        """Move credential to first position (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_id: Credential ID to move to first
            
        Raises:
            APIError: If moving credential fails
        """
        response = self._sync(
            post_admin_realms_realm_users_user_id_credentials_credential_id_move_to_first.sync_detailed,
            realm,
            user_id=user_id,
            credential_id=credential_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to move credential to first: {response.status_code}")

    async def amove_credential_to_first(self, realm: str | None = None, *, user_id: str, credential_id: str) -> None:
        """Move credential to first position (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_id: Credential ID to move to first
            
        Raises:
            APIError: If moving credential fails
        """
        response = await self._async(
            post_admin_realms_realm_users_user_id_credentials_credential_id_move_to_first.asyncio_detailed,
            realm,
            user_id=user_id,
            credential_id=credential_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to move credential to first: {response.status_code}")

    def disable_credential_types(self, realm: str | None = None, *, user_id: str, credential_types: list[str]) -> None:
        """Disable credential types for user (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_types: List of credential types to disable
            
        Raises:
            APIError: If disabling credential types fails
        """
        response = self._sync_detailed(
            put_admin_realms_realm_users_user_id_disable_credential_types.sync_detailed,
            realm,
            user_id=user_id,
            body=credential_types,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to disable credential types: {response.status_code}")

    async def adisable_credential_types(self, realm: str | None = None, *, user_id: str, credential_types: list[str]) -> None:
        """Disable credential types for user (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            credential_types: List of credential types to disable
            
        Raises:
            APIError: If disabling credential types fails
        """
        response = await self._async_detailed(
            put_admin_realms_realm_users_user_id_disable_credential_types.asyncio_detailed,
            realm,
            user_id=user_id,
            body=credential_types,
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to disable credential types: {response.status_code}")

    def reset_password_email(self, realm: str | None = None, *, user_id: str, redirect_uri: str | None = None, client_id: str | None = None) -> None:
        """Send reset password email (sync).
        
        Args:
            realm: The realm name
            user_id: User ID
            redirect_uri: URL to redirect to after password reset
            client_id: Client ID initiating the reset
            
        Raises:
            APIError: If sending reset password email fails
        """
        response = self._sync(
            put_admin_realms_realm_users_user_id_reset_password_email.sync_detailed,
            realm,
            user_id=user_id,
            redirect_uri=redirect_uri,
            client_id=client_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to send reset password email: {response.status_code}")

    async def areset_password_email(self, realm: str | None = None, *, user_id: str, redirect_uri: str | None = None, client_id: str | None = None) -> None:
        """Send reset password email (async).
        
        Args:
            realm: The realm name
            user_id: User ID
            redirect_uri: URL to redirect to after password reset
            client_id: Client ID initiating the reset
            
        Raises:
            APIError: If sending reset password email fails
        """
        response = await self._async(
            put_admin_realms_realm_users_user_id_reset_password_email.asyncio_detailed,
            realm,
            user_id=user_id,
            redirect_uri=redirect_uri,
            client_id=client_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to send reset password email: {response.status_code}")

    def get_profile(self, realm: str | None = None) -> UPConfig | None:
        """Get users profile (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            User profile configuration for the realm
        """
        return self._sync(
            get_admin_realms_realm_users_profile.sync,
            realm,
        )

    async def aget_profile(self, realm: str | None = None) -> UPConfig | None:
        """Get users profile (async).
        
        Args:
            realm: The realm name
            
        Returns:
            User profile configuration for the realm
        """
        return await self._async(
            get_admin_realms_realm_users_profile.asyncio,
            realm,
        )

    def update_profile(self, realm: str | None = None, *, profile_data: dict | UPConfig) -> None:
        """Update users profile (sync).
        
        Args:
            realm: The realm name
            profile_data: Updated user profile configuration
            
        Raises:
            APIError: If profile update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_users_profile.sync_detailed,
            realm,
            profile_data,
            UPConfig
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update profile: {response.status_code}")

    async def aupdate_profile(self, realm: str | None = None, *, profile_data: dict | UPConfig) -> None:
        """Update users profile (async).
        
        Args:
            realm: The realm name
            profile_data: Updated user profile configuration
            
        Raises:
            APIError: If profile update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_users_profile.asyncio_detailed,
            realm,
            profile_data,
            UPConfig
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update profile: {response.status_code}")

    def get_profile_metadata(self, realm: str | None = None) -> UserProfileMetadata | None:
        """Get users profile metadata (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            User profile metadata including attribute definitions
        """
        return self._sync(
            get_admin_realms_realm_users_profile_metadata.sync,
            realm,
        )

    async def aget_profile_metadata(self, realm: str | None = None) -> UserProfileMetadata | None:
        """Get users profile metadata (async).
        
        Args:
            realm: The realm name
            
        Returns:
            User profile metadata including attribute definitions
        """
        return await self._async(
            get_admin_realms_realm_users_profile_metadata.asyncio,
            realm,
        )


class UsersClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the UsersAPI."""
    
    @cached_property
    def users(self) -> UsersAPI:
        """Get the UsersAPI instance.
        
        Returns:
            UsersAPI instance for managing users
        """
        return UsersAPI(manager=self)  # type: ignore[arg-type]
