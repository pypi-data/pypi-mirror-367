"""
Keycloak client that provides a clean interface over the generated code.

This handles authentication and provides proper sync/async support without
requiring separate client classes.
"""
from urllib.parse import urlencode, urljoin

from .api import KeycloakClientMixin
from .base import BaseKeycloakClient

__all__ = "KeycloakClient",


class KeycloakClient(KeycloakClientMixin, BaseKeycloakClient):
    """A unified Keycloak client that handles both sync and async operations.

    This client:
    - Auto-authenticates using environment variables or provided credentials
    - Provides a single interface for both sync and async operations
    - Handles token refresh automatically
    - Exposes the full generated API while adding convenience
    
    Usage:
        # Sync usage
        client = KeycloakClient()
        users = client.users.get_all("master")
        
        # Async usage
        async with client:
            users = await client.users.aget_all("master")

        # Direct access to generated API still works (not recommended for most use cases):
        from ackc.generated.api.users import get_admin_realms_realm_users
        users = get_admin_realms_realm_users.sync(realm="master", client=client._client)
    """

    def _build_url(self, path: str, **params) -> str:
        """Build a complete URL with server, path, and optional query parameters.
        
        Args:
            path: The URL path (relative to server_url)
            **params: Optional query parameters as keyword arguments
            
        Returns:
            The complete URL with encoded query parameters
        """
        full_url = urljoin(self.server_url, path.lstrip("/"))

        filtered_params = {k: v for k, v in params.items() if v is not None}
        if filtered_params:
            return f"{full_url}?{urlencode(filtered_params)}"
        return full_url

    def get_login_url(self, realm: str | None = None, **params) -> str:
        """Get the login URL for a specific realm.

        Args:
            realm: The realm name (defaults to instance realm)
            **params: Additional query parameters (e.g., client_id, response_type, scope, state)

        Returns:
            The login URL for the specified realm
        """
        return self._build_url(f"realms/{realm or self.realm}/protocol/openid-connect/auth", **params)

    @property
    def login_url(self) -> str:
        """Get the login URL for the default realm.

        Returns:
            The login URL for the default realm
        """
        return self.get_login_url(self.realm)

    @property
    def auth_login_url(self) -> str:
        """Get the login URL for the authentication realm.

        Returns:
            The login URL for the authentication realm (typically "master")
        """
        return self.get_login_url(self.auth_realm)

    def check_registration_enabled(self, realm: str | None = None) -> bool:
        """Check if registration is enabled for a specific realm.

        Args:
            realm: The realm name (defaults to instance realm)

        Returns:
            True if registration is enabled, False otherwise
        """
        realm_data = self.realms.get(realm or self.realm)
        return bool(realm_data and getattr(realm_data, "registration_allowed", False))

    async def acheck_registration_enabled(self, realm: str | None = None) -> bool:
        """Check if registration is enabled for a specific realm (async).

        Args:
            realm: The realm name (defaults to instance realm)

        Returns:
            True if registration is enabled, False otherwise
        """
        realm_data = await self.realms.aget(realm or self.realm)
        return bool(realm_data and getattr(realm_data, "registration_allowed", False))

    def get_registration_url(self, realm: str | None = None, *, redirect_uri: str | None = None) -> str:
        """Get the registration URL for a specific realm if registration is enabled.

        Does not guarantee that registration is enabled; use `check_registration_enabled` first.

        Args:
            realm: The realm name (defaults to instance realm)
            redirect_uri: Optional redirect URI after successful registration

        Returns:
            The registration URL for the specified realm
        """
        return self._build_url(f"realms/{realm or self.realm}/protocol/openid-connect/registrations", redirect_uri=redirect_uri)

    @property
    def registration_url(self) -> str | None:
        """Get the registration URL for the default realm if registration is enabled.

        Returns:
            The registration URL for the default realm, or None if registration is disabled
        """
        return self.get_registration_url(self.realm)

    def export_realm_config(self, realm: str | None = None, *, include_users: bool = False) -> dict:
        """Export complete realm configuration for backup or migration.

        Uses Keycloak's native partial export endpoint which includes all realm
        settings, clients, roles, groups, identity providers, authentication flows,
        and more. Optionally adds users (not included in native export).

        Args:
            realm: Realm name to export (defaults to instance realm)
            include_users: Whether to include users in export (can be large)

        Returns:
            Dictionary containing full realm configuration
        """
        realm = realm or self.realm
        
        realm_rep = self.realms.partial_export(
            realm=realm,
            export_clients=True,
            export_groups_and_roles=True
        )
        config = realm_rep.to_dict() if realm_rep else {}
        
        if include_users:
            users = self.users.get_all(realm, brief_representation=False) or []
            config["users"] = [u.to_dict() for u in users]

        return config

    async def aexport_realm_config(self, realm: str | None = None, *, include_users: bool = False) -> dict:
        """Export complete realm configuration for backup or migration (async).
        
        Uses Keycloak's native partial export endpoint which includes all realm
        settings, clients, roles, groups, identity providers, authentication flows,
        and more. Optionally adds users (not included in native export).
        
        Args:
            realm: Realm name to export (defaults to instance realm)
            include_users: Whether to include users in export (can be large)
            
        Returns:
            Dictionary containing full realm configuration
        """
        realm = realm or self.realm
        
        realm_rep = await self.realms.apartial_export(
            realm=realm,
            export_clients=True,
            export_groups_and_roles=True
        )
        config = realm_rep.to_dict() if realm_rep else {}
        
        if include_users:
            users = await self.users.aget_all(realm, brief_representation=False) or []
            config["users"] = [u.to_dict() for u in users]

        return config
