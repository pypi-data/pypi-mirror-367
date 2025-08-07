"""Client registration policy API methods."""
from functools import cached_property

from .base import BaseAPI
from ..generated.api.client_registration_policy import (
    get_admin_realms_realm_client_registration_policy_providers,
)
from ..generated.models import ComponentTypeRepresentation

__all__ = "ClientRegistrationPolicyAPI", "ClientRegistrationPolicyClientMixin"


class ClientRegistrationPolicyAPI(BaseAPI):
    """Client registration policy API methods."""

    def get_providers(self, realm: str | None = None) -> list[ComponentTypeRepresentation] | None:
        """Get client registration policy providers.
        
        Lists available policy providers for client registration.
        
        Args:
            realm: The realm name
            
        Returns:
            List of available policy provider types
        """
        return self._sync(
            get_admin_realms_realm_client_registration_policy_providers.sync,
            realm
        )

    async def aget_providers(self, realm: str | None = None) -> list[ComponentTypeRepresentation] | None:
        """Get client registration policy providers (async).
        
        Lists available policy providers for client registration.
        
        Args:
            realm: The realm name
            
        Returns:
            List of available policy provider types
        """
        return await self._async(
            get_admin_realms_realm_client_registration_policy_providers.asyncio,
            realm
        )


class ClientRegistrationPolicyClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ClientRegistrationPolicyAPI."""
    
    @cached_property
    def client_registration_policy(self) -> ClientRegistrationPolicyAPI:
        """Get the ClientRegistrationPolicyAPI instance."""
        return ClientRegistrationPolicyAPI(manager=self)  # type: ignore[arg-type]