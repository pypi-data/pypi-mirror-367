"""Token acquisition utility functions.

This module provides reusable functions for obtaining Keycloak tokens
via various OAuth2 flows. These functions can be used programmatically
or through the CLI tool.
"""
from . import env
from .keycloak import KeycloakClient

__all__ = (
    "default_client_factory",
    "get_token_device",
    "get_token_password",
    "get_token_client_credentials",
    "get_token_refresh",
)


def default_client_factory(*, server_url=None, realm=None, client_id=None, client_secret=None, auth_realm=None) -> KeycloakClient:
    """Default factory for creating KeycloakClient instances from env vars.
    
    By default, auth_realm (where the client authenticates) matches realm (where users are).
    This is the common case where your client is registered in the same realm as your users.
    """
    return KeycloakClient(
        server_url=server_url or env.KEYCLOAK_URL,
        realm=realm or env.KEYCLOAK_REALM,
        auth_realm=auth_realm or env.KEYCLOAK_AUTH_REALM,
        client_id=client_id or env.KEYCLOAK_CLIENT_ID,
        client_secret=client_secret or env.KEYCLOAK_CLIENT_SECRET,
    )


def get_token_device(
    *,
    callback,
    server_url=None,
    realm=None,
    client_id=None,
    auth_realm=None,
    scopes=None,
    client_factory=None,
):
    """Get token using device authorization flow.
    
    Args:
        server_url: Keycloak server URL
        realm: Realm name
        client_id: Client ID
        auth_realm: Authentication realm
        scopes: OAuth2 scopes to request
        callback: Callback function that receives verification_uri, user_code, and expires_in
        client_factory: Factory function for creating KeycloakClient instances
        
    Returns:
        Token dict with access_token, refresh_token, etc.
    """
    if client_factory is None:
        client_factory = default_client_factory

    client = client_factory(
        server_url=server_url,
        realm=realm,
        auth_realm=auth_realm,
        client_id=client_id,
        client_secret=None,  # Device flow typically uses public clients
    )

    return client.get_token_device(callback=callback, scopes=scopes)


def get_token_password(
    *,
    username,
    password,
    otp=None,
    server_url=None,
    realm=None,
    client_id=None,
    client_secret=None,
    auth_realm=None,
    scopes=None,
    client_factory=None,
):
    """Get token using password grant.
    
    Args:
        username: Username
        password: Password
        otp: Optional OTP/2FA code (will be concatenated with password)
        server_url: Keycloak server URL
        realm: Realm name
        client_id: Client ID
        client_secret: Client secret
        auth_realm: Authentication realm
        scopes: OAuth2 scopes to request
        client_factory: Factory function for creating KeycloakClient instances
        
    Returns:
        Token dict with access_token, refresh_token, etc.
    """

    if client_factory is None:
        client_factory = default_client_factory

    client = client_factory(
        server_url=server_url,
        realm=realm,
        auth_realm=auth_realm,
        client_id=client_id,
        client_secret=client_secret,
    )

    return client.get_token_password(
        username=username,
        password=password,
        otp=otp,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes
    )


def get_token_client_credentials(*, server_url=None, realm=None, client_id=None, client_secret=None, auth_realm=None, scopes=None, client_factory=None):
    """Get token using client credentials grant.
    
    Args:
        server_url: Keycloak server URL
        realm: Realm name
        client_id: Client ID
        client_secret: Client secret
        auth_realm: Authentication realm
        scopes: OAuth2 scopes to request
        client_factory: Factory function for creating KeycloakClient instances
        
    Returns:
        Token dict with access_token, refresh_token, etc.
    """
    if client_factory is None:
        client_factory = default_client_factory

    client = client_factory(
        server_url=server_url,
        realm=realm,
        auth_realm=auth_realm,
        client_id=client_id,
        client_secret=client_secret,
    )
    return client.get_token(scopes=scopes)


def get_token_refresh(
    *,
    refresh_token,
    server_url=None,
    realm=None,
    client_id=None,
    client_secret=None,
    auth_realm=None,
    client_factory=None,
):
    """Refresh an existing token.
    
    Args:
        server_url: Keycloak server URL
        realm: Realm name
        refresh_token: The refresh token to exchange
        client_id: Client ID
        client_secret: Client secret
        auth_realm: Authentication realm
        client_factory: Factory function for creating KeycloakClient instances
        
    Returns:
        New token dict with access_token, refresh_token, etc.
    """

    if client_factory is None:
        client_factory = default_client_factory

    client = client_factory(
        server_url=server_url,
        realm=realm,
        auth_realm=auth_realm,
        client_id=client_id,
        client_secret=client_secret,
    )

    return client.jwt_refresh(refresh_token=refresh_token)
