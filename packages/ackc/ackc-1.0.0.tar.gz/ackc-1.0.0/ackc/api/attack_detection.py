"""Attack detection API methods."""
from functools import cached_property
from typing import Any

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.attack_detection import (
    get_admin_realms_realm_attack_detection_brute_force_users_user_id,
    delete_admin_realms_realm_attack_detection_brute_force_users,
    delete_admin_realms_realm_attack_detection_brute_force_users_user_id,
)

__all__ = "AttackDetectionAPI", "AttackDetectionClientMixin"


class AttackDetectionAPI(BaseAPI):
    """Attack detection API methods."""

    def get_brute_force_user_status(self, realm: str | None = None, *, user_id: str) -> dict[str, Any] | None:
        """Get brute force detection status for a specific user.
        
        Args:
            realm: The realm name
            user_id: User ID to check
            
        Returns:
            Dictionary with brute force status including failed login count and disabled status
        """
        return self._sync_ap(
            get_admin_realms_realm_attack_detection_brute_force_users_user_id.sync,
            realm,
            user_id=user_id
        )

    async def aget_brute_force_user_status(self, realm: str | None = None, *, user_id: str) -> dict[str, Any] | None:
        """Get brute force detection status for a specific user (async).
        
        Args:
            realm: The realm name
            user_id: User ID to check
            
        Returns:
            Dictionary with brute force status including failed login count and disabled status
        """
        return await self._async_ap(
            get_admin_realms_realm_attack_detection_brute_force_users_user_id.asyncio,
            realm,
            user_id=user_id
        )

    def clear_all_brute_force_users(self, realm: str | None = None) -> None:
        """Clear brute force attempts for all users in the realm.
        
        Resets the failed login count for all users who have been locked out.
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If clearing brute force data fails
        """
        response = self._sync(
            delete_admin_realms_realm_attack_detection_brute_force_users.sync_detailed,
            realm
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to clear brute force users: {response.status_code}")

    async def aclear_all_brute_force_users(self, realm: str | None = None) -> None:
        """Clear brute force attempts for all users in the realm (async).
        
        Resets the failed login count for all users who have been locked out.
        
        Args:
            realm: The realm name
            
        Raises:
            APIError: If clearing brute force data fails
        """
        response = await self._async(
            delete_admin_realms_realm_attack_detection_brute_force_users.asyncio_detailed,
            realm
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to clear brute force users: {response.status_code}")

    def clear_brute_force_user(self, realm: str | None = None, *, user_id: str) -> None:
        """Clear brute force attempts for a specific user.
        
        Resets the failed login count and re-enables the user if locked out.
        
        Args:
            realm: The realm name
            user_id: User ID to clear
            
        Raises:
            APIError: If clearing brute force data fails
        """
        response = self._sync(
            delete_admin_realms_realm_attack_detection_brute_force_users_user_id.sync_detailed,
            realm,
            user_id=user_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to clear brute force user: {response.status_code}")

    async def aclear_brute_force_user(self, realm: str | None = None, *, user_id: str) -> None:
        """Clear brute force attempts for a specific user (async).
        
        Resets the failed login count and re-enables the user if locked out.
        
        Args:
            realm: The realm name
            user_id: User ID to clear
            
        Raises:
            APIError: If clearing brute force data fails
        """
        response = await self._async(
            delete_admin_realms_realm_attack_detection_brute_force_users_user_id.asyncio_detailed,
            realm,
            user_id=user_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to clear brute force user: {response.status_code}")


class AttackDetectionClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the AttackDetectionAPI."""
    
    @cached_property
    def attack_detection(self) -> AttackDetectionAPI:
        """Get the AttackDetectionAPI instance."""
        return AttackDetectionAPI(manager=self)  # type: ignore[arg-type]