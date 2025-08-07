"""Component management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.component import (
    get_admin_realms_realm_components,
    post_admin_realms_realm_components,
    get_admin_realms_realm_components_id,
    put_admin_realms_realm_components_id,
    delete_admin_realms_realm_components_id,
    get_admin_realms_realm_components_id_sub_component_types,
)
from ..generated.models import ComponentRepresentation, ComponentTypeRepresentation
from ..generated.types import UNSET, Unset

__all__ = "ComponentsAPI", "ComponentsClientMixin", "ComponentRepresentation", "ComponentTypeRepresentation"


class ComponentsAPI(BaseAPI):
    """Component management API methods."""

    def get_all(
        self,
        realm: str | None = None,
        *,
        name: Unset | str = UNSET,
        parent: Unset | str = UNSET,
        type: Unset | str = UNSET,
    ) -> list[ComponentRepresentation] | None:
        """List components in a realm.
        
        Args:
            realm: The realm name
            name: Filter by component name
            parent: Filter by parent ID
            type: Filter by component type
            
        Returns:
            List of components matching the filters
        """
        return self._sync(
            get_admin_realms_realm_components.sync,
            realm,
            name=name,
            parent=parent,
            type_=type,
        )

    async def aget_all(
        self,
        realm: str | None = None,
        *,
        name: Unset | str = UNSET,
        parent: Unset | str = UNSET,
        type: Unset | str = UNSET,
    ) -> list[ComponentRepresentation] | None:
        """List components in a realm (async).
        
        Args:
            realm: The realm name
            name: Filter by component name
            parent: Filter by parent ID
            type: Filter by component type
            
        Returns:
            List of components matching the filters
        """
        return await self._async(
            get_admin_realms_realm_components.asyncio,
            realm,
            name=name,
            parent=parent,
            type_=type,
        )

    def create(self, realm: str | None = None, *, component_data: dict | ComponentRepresentation) -> str:
        """Create a component (sync).
        
        Components are pluggable providers like user storage, key providers, etc.
        
        Args:
            realm: The realm name
            component_data: Component configuration
            
        Returns:
            Created component ID
            
        Raises:
            APIError: If component creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_components.sync_detailed,
            realm,
            component_data,
            ComponentRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create component: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def acreate(self, realm: str | None = None, *, component_data: dict | ComponentRepresentation) -> str:
        """Create a component (async).
        
        Components are pluggable providers like user storage, key providers, etc.
        
        Args:
            realm: The realm name
            component_data: Component configuration
            
        Returns:
            Created component ID
            
        Raises:
            APIError: If component creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_components.asyncio_detailed,
            realm,
            component_data,
            ComponentRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create component: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def get(self, realm: str | None = None, *, component_id: str) -> ComponentRepresentation | None:
        """Get a component by ID (sync).
        
        Args:
            realm: The realm name
            component_id: Component ID
            
        Returns:
            Component configuration and metadata
        """
        return self._sync(
            get_admin_realms_realm_components_id.sync,
            realm,
            id=component_id
        )

    async def aget(self, realm: str | None = None, *, component_id: str) -> ComponentRepresentation | None:
        """Get a component by ID (async).
        
        Args:
            realm: The realm name
            component_id: Component ID
            
        Returns:
            Component configuration and metadata
        """
        return await self._async(
            get_admin_realms_realm_components_id.asyncio,
            realm,
            id=component_id
        )

    def update(self, realm: str | None = None, *, component_id: str, component_data: dict | ComponentRepresentation) -> None:
        """Update a component (sync).
        
        Args:
            realm: The realm name
            component_id: Component ID to update
            component_data: Updated component configuration
            
        Raises:
            APIError: If component update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_components_id.sync_detailed,
            realm,
            component_data,
            ComponentRepresentation,
            id=component_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update component: {response.status_code}")

    async def aupdate(self, realm: str | None = None, *, component_id: str, component_data: dict | ComponentRepresentation) -> None:
        """Update a component (async).
        
        Args:
            realm: The realm name
            component_id: Component ID to update
            component_data: Updated component configuration
            
        Raises:
            APIError: If component update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_components_id.asyncio_detailed,
            realm,
            component_data,
            ComponentRepresentation,
            id=component_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update component: {response.status_code}")

    def delete(self, realm: str | None = None, *, component_id: str) -> None:
        """Delete a component (sync).
        
        Args:
            realm: The realm name
            component_id: Component ID to delete
            
        Raises:
            APIError: If component deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_components_id.sync_detailed,
            realm,
            id=component_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete component: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, component_id: str) -> None:
        """Delete a component (async).
        
        Args:
            realm: The realm name
            component_id: Component ID to delete
            
        Raises:
            APIError: If component deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_components_id.asyncio_detailed,
            realm,
            id=component_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete component: {response.status_code}")

    def get_sub_component_types(self, realm: str | None = None, *, component_id: str, type: Unset | str = UNSET) -> list[ComponentTypeRepresentation] | None:
        """Get sub-component types (sync).
        
        Args:
            realm: The realm name
            component_id: Parent component ID
            type: Optional type filter
            
        Returns:
            List of available sub-component types
        """
        return self._sync(
            get_admin_realms_realm_components_id_sub_component_types.sync,
            realm,
            id=component_id,
            type_=type
        )

    async def aget_sub_component_types(self, realm: str | None = None, *, component_id: str, type: Unset | str = UNSET) -> list[ComponentTypeRepresentation] | None:
        """Get sub-component types (async).
        
        Args:
            realm: The realm name
            component_id: Parent component ID
            type: Optional type filter
            
        Returns:
            List of available sub-component types
        """
        return await self._async(
            get_admin_realms_realm_components_id_sub_component_types.asyncio,
            realm,
            id=component_id,
            type_=type
        )


class ComponentsClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ComponentsAPI.
    """

    @cached_property
    def components(self) -> ComponentsAPI:
        """Get the ComponentsAPI instance."""
        return ComponentsAPI(manager=self)  # type: ignore[arg-type]
