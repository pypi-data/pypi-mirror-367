"""Key management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..generated.api.key import get_admin_realms_realm_keys
from ..generated.models import KeysMetadataRepresentation

__all__ = "KeysAPI", "KeysClientMixin", "KeysMetadataRepresentation"


class KeysAPI(BaseAPI):
    """Key management API methods for realm cryptographic keys."""

    def get_keys(self, realm: str | None = None) -> KeysMetadataRepresentation | None:
        """Get keys metadata for a realm (sync).
        
        Returns metadata about the realm's cryptographic keys including:
        - Active keys for signing
        - Passive keys for verification
        - Key algorithms and providers
        
        Args:
            realm: The realm name
            
        Returns:
            Keys metadata including active, passive, and disabled keys
        """
        return self._sync(get_admin_realms_realm_keys.sync, realm)

    async def aget_keys(self, realm: str | None = None) -> KeysMetadataRepresentation | None:
        """Get keys metadata for a realm (async).
        
        Returns metadata about the realm's cryptographic keys including:
        - Active keys for signing
        - Passive keys for verification  
        - Key algorithms and providers
        
        Args:
            realm: The realm name
            
        Returns:
            Keys metadata including active, passive, and disabled keys
        """
        return await self._async(get_admin_realms_realm_keys.asyncio, realm)


class KeysClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the KeysAPI.
    """

    @cached_property
    def keys(self) -> KeysAPI:
        """Get the KeysAPI instance."""
        return KeysAPI(manager=self)  # type: ignore[arg-type]
