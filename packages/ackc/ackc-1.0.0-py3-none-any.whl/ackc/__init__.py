"""ACKC - Keycloak API client using niquests.
"""
from importlib.metadata import version

from .generated import AuthenticatedClient, Client
from .generated import models

from .keycloak import KeycloakClient
from .management import KeycloakManagementClient, HealthStatus, HealthCheck, HealthResponse
from .exceptions import (
    AuthError,
    ClientError,
    TokenExpiredError,
    InvalidTokenError,
    UserNotFoundError,
    RealmNotFoundError,
    ClientNotFoundError,
    APIError,
)

__version__ = version("ackc")

__all__ = (
    # Generated exports
    "AuthenticatedClient",
    "Client",
    "models",
    # Our wrapper
    "KeycloakClient",
    # Management client
    "KeycloakManagementClient",
    "HealthStatus",
    "HealthCheck",
    "HealthResponse",
    # Exceptions
    "AuthError",
    "ClientError",
    "TokenExpiredError",
    "InvalidTokenError",
    "UserNotFoundError",
    "RealmNotFoundError",
    "ClientNotFoundError",
    "APIError",
)
