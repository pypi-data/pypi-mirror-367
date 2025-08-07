"""Custom exceptions.
"""


class ClientError(Exception):
    """Base exception for all client errors."""
    pass


class AuthError(ClientError):
    """Authentication/authorization error."""
    pass


class TokenExpiredError(AuthError):
    """Access token has expired."""
    pass


class InvalidTokenError(AuthError):
    """Token is invalid or malformed."""
    pass


class UserNotFoundError(ClientError):
    """User not found in Keycloak."""
    pass


class RealmNotFoundError(ClientError):
    """Realm not found in Keycloak."""
    pass


class ClientNotFoundError(ClientError):
    """Client not found in Keycloak."""
    pass


class APIError(ClientError):
    """General API operation error."""
    pass
