
""" A client library for accessing Keycloak Admin REST API """
from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
