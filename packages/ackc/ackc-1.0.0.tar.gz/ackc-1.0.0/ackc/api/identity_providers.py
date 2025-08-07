"""Identity provider management API methods."""
import json
from functools import cached_property
from typing import Any

from .base import BaseAPI
from ..exceptions import APIError
from ..generated.api.identity_providers import (
    get_admin_realms_realm_identity_provider_instances,
    post_admin_realms_realm_identity_provider_instances,
    get_admin_realms_realm_identity_provider_instances_alias,
    put_admin_realms_realm_identity_provider_instances_alias,
    delete_admin_realms_realm_identity_provider_instances_alias,
    get_admin_realms_realm_identity_provider_instances_alias_mappers,
    post_admin_realms_realm_identity_provider_instances_alias_mappers,
    get_admin_realms_realm_identity_provider_instances_alias_mappers_id,
    put_admin_realms_realm_identity_provider_instances_alias_mappers_id,
    delete_admin_realms_realm_identity_provider_instances_alias_mappers_id,
    get_admin_realms_realm_identity_provider_instances_alias_mapper_types,
    get_admin_realms_realm_identity_provider_instances_alias_export,
    post_admin_realms_realm_identity_provider_import_config,
)
from ..generated.models import IdentityProviderRepresentation, IdentityProviderMapperRepresentation

__all__ = "IdentityProvidersAPI", "IdentityProvidersClientMixin", "IdentityProviderRepresentation"


class IdentityProvidersAPI(BaseAPI):
    """Identity provider management API methods."""

    def get_all(self, realm: str | None = None) -> list[IdentityProviderRepresentation] | None:
        """List identity providers in a realm (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of configured identity providers (Google, SAML, OIDC, etc.)
        """
        return self._sync(get_admin_realms_realm_identity_provider_instances.sync, realm)

    async def aget_all(self, realm: str | None = None) -> list[IdentityProviderRepresentation] | None:
        """List identity providers in a realm (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of configured identity providers (Google, SAML, OIDC, etc.)
        """
        return await self._async(get_admin_realms_realm_identity_provider_instances.asyncio, realm)

    def create(self, realm: str | None = None, *, provider_data: dict | IdentityProviderRepresentation) -> None:
        """Create an identity provider (sync).
        
        Args:
            realm: The realm name
            provider_data: Identity provider configuration
            
        Raises:
            APIError: If creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_identity_provider_instances.sync_detailed,
            realm,
            provider_data,
            IdentityProviderRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create identity provider: {response.status_code}")

    async def acreate(self, realm: str | None = None, *, provider_data: dict | IdentityProviderRepresentation) -> None:
        """Create an identity provider (async).
        
        Args:
            realm: The realm name
            provider_data: Identity provider configuration
            
        Raises:
            APIError: If creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_identity_provider_instances.asyncio_detailed,
            realm,
            provider_data,
            IdentityProviderRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create identity provider: {response.status_code}")

    def get(self, realm: str | None = None, *, alias: str) -> IdentityProviderRepresentation | None:
        """Get an identity provider by alias (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            
        Returns:
            Identity provider configuration
        """
        return self._sync(
            get_admin_realms_realm_identity_provider_instances_alias.sync,
            realm,
            alias=alias
        )

    async def aget(self, realm: str | None = None, *, alias: str) -> IdentityProviderRepresentation | None:
        """Get an identity provider by alias (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            
        Returns:
            Identity provider configuration
        """
        return await self._async(
            get_admin_realms_realm_identity_provider_instances_alias.asyncio,
            realm,
            alias=alias
        )

    def update(self, realm: str | None = None, *, alias: str, provider_data: dict | IdentityProviderRepresentation) -> None:
        """Update an identity provider (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            provider_data: Updated provider configuration
            
        Raises:
            APIError: If update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_identity_provider_instances_alias.sync_detailed,
            realm,
            provider_data,
            IdentityProviderRepresentation,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update identity provider: {response.status_code}")

    async def aupdate(self, realm: str | None = None, *, alias: str, provider_data: dict | IdentityProviderRepresentation) -> None:
        """Update an identity provider (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            provider_data: Updated provider configuration
            
        Raises:
            APIError: If update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_identity_provider_instances_alias.asyncio_detailed,
            realm,
            provider_data,
            IdentityProviderRepresentation,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update identity provider: {response.status_code}")

    def delete(self, realm: str | None = None, *, alias: str) -> None:
        """Delete an identity provider (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_identity_provider_instances_alias.sync_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete identity provider: {response.status_code}")

    async def adelete(self, realm: str | None = None, *, alias: str) -> None:
        """Delete an identity provider (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_identity_provider_instances_alias.asyncio_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete identity provider: {response.status_code}")

    def get_mappers(self, realm: str | None = None, *, alias: str) -> list[IdentityProviderMapperRepresentation] | None:
        """Get identity provider mappers (sync).
        
        Mappers define how external identity provider data maps to Keycloak user attributes.
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            
        Returns:
            List of configured mappers for the identity provider
        """
        return self._sync(
            get_admin_realms_realm_identity_provider_instances_alias_mappers.sync,
            realm,
            alias=alias
        )

    async def aget_mappers(self, realm: str | None = None, *, alias: str) -> list[IdentityProviderMapperRepresentation] | None:
        """Get identity provider mappers (async).
        
        Mappers define how external identity provider data maps to Keycloak user attributes.
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            
        Returns:
            List of configured mappers for the identity provider
        """
        return await self._async(
            get_admin_realms_realm_identity_provider_instances_alias_mappers.asyncio,
            realm,
            alias=alias
        )

    def create_mapper(
        self,
        realm: str | None = None,
        *,
        alias: str,
        mapper_data: dict | IdentityProviderMapperRepresentation
    ) -> str:
        """Create identity provider mapper (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_data: Mapper configuration
            
        Returns:
            Created mapper ID
            
        Raises:
            APIError: If mapper creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_identity_provider_instances_alias_mappers.sync_detailed,
            realm,
            mapper_data,
            IdentityProviderMapperRepresentation,
            alias=alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create mapper: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def acreate_mapper(
        self,
        realm: str | None = None,
        *,
        alias: str,
        mapper_data: dict | IdentityProviderMapperRepresentation
    ) -> str:
        """Create identity provider mapper (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_data: Mapper configuration
            
        Returns:
            Created mapper ID
            
        Raises:
            APIError: If mapper creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_identity_provider_instances_alias_mappers.asyncio_detailed,
            realm,
            mapper_data,
            IdentityProviderMapperRepresentation,
            alias=alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create mapper: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def get_mapper(self, realm: str | None = None, *, alias: str, mapper_id: str) -> IdentityProviderMapperRepresentation | None:
        """Get identity provider mapper (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_id: Mapper ID
            
        Returns:
            Mapper configuration
        """
        return self._sync(
            get_admin_realms_realm_identity_provider_instances_alias_mappers_id.sync,
            realm,
            alias=alias,
            id=mapper_id
        )

    async def aget_mapper(self, realm: str | None = None, *, alias: str, mapper_id: str) -> IdentityProviderMapperRepresentation | None:
        """Get identity provider mapper (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_id: Mapper ID
            
        Returns:
            Mapper configuration
        """
        return await self._async(
            get_admin_realms_realm_identity_provider_instances_alias_mappers_id.asyncio,
            realm,
            alias=alias,
            id=mapper_id
        )

    def update_mapper(
        self,
        realm: str | None = None,
        *,
        alias: str,
        mapper_id: str,
        mapper_data: dict | IdentityProviderMapperRepresentation
    ) -> None:
        """Update identity provider mapper (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_id: Mapper ID to update
            mapper_data: Updated mapper configuration
            
        Raises:
            APIError: If mapper update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_identity_provider_instances_alias_mappers_id.sync_detailed,
            realm,
            mapper_data,
            IdentityProviderMapperRepresentation,
            alias=alias,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update mapper: {response.status_code}")

    async def aupdate_mapper(
        self,
        realm: str | None = None,
        *,
        alias: str,
        mapper_id: str,
        mapper_data: dict | IdentityProviderMapperRepresentation
    ) -> None:
        """Update identity provider mapper (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_id: Mapper ID to update
            mapper_data: Updated mapper configuration
            
        Raises:
            APIError: If mapper update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_identity_provider_instances_alias_mappers_id.asyncio_detailed,
            realm,
            mapper_data,
            IdentityProviderMapperRepresentation,
            alias=alias,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update mapper: {response.status_code}")

    def delete_mapper(self, realm: str | None = None, *, alias: str, mapper_id: str) -> None:
        """Delete identity provider mapper (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_id: Mapper ID to delete
            
        Raises:
            APIError: If mapper deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_identity_provider_instances_alias_mappers_id.sync_detailed,
            realm,
            alias=alias,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete mapper: {response.status_code}")

    async def adelete_mapper(self, realm: str | None = None, *, alias: str, mapper_id: str) -> None:
        """Delete identity provider mapper (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            mapper_id: Mapper ID to delete
            
        Raises:
            APIError: If mapper deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_identity_provider_instances_alias_mappers_id.asyncio_detailed,
            realm,
            alias=alias,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete mapper: {response.status_code}")

    def get_mapper_types(self, realm: str | None = None, *, alias: str) -> dict[str, Any] | None:
        """Get available mapper types (sync).
        
        NOTE: This endpoint's OpenAPI spec is broken - it doesn't define a response schema.
        The actual response needs to be manually extracted from the HTTP response.
        TODO: Verify actual Keycloak API response format and report OpenAPI spec issue if needed.
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            
        Returns:
            Dictionary of available mapper types and their configurations
        """
        response = self._sync_detailed(
            get_admin_realms_realm_identity_provider_instances_alias_mapper_types.sync_detailed,
            realm,
            alias=alias
        )
        if response.status_code == 200:
            return json.loads(response.content)
        return None

    async def aget_mapper_types(self, realm: str | None = None, *, alias: str) -> dict[str, Any] | None:
        """Get available mapper types (async).
        
        NOTE: This endpoint's OpenAPI spec is broken - it doesn't define a response schema.
        The actual response needs to be manually extracted from the HTTP response.
        TODO: Verify actual Keycloak API response format and report OpenAPI spec issue if needed.
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            
        Returns:
            Dictionary of available mapper types and their configurations
        """
        response = await self._async_detailed(
            get_admin_realms_realm_identity_provider_instances_alias_mapper_types.asyncio_detailed,
            realm,
            alias=alias
        )
        if response.status_code == 200:
            return json.loads(response.content)
        return None

    def export(self, realm: str | None = None, *, alias: str, format: str | None = None) -> str | None:
        """Export identity provider configuration (sync).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            format: Export format (e.g., 'json', 'saml-metadata')
            
        Returns:
            Exported configuration in requested format
        """
        response = self._sync_detailed(
            get_admin_realms_realm_identity_provider_instances_alias_export.sync_detailed,
            realm,
            alias=alias,
            format_=format,
        )
        if response.status_code == 200:
            return response.content.decode('utf-8') if response.content else None
        return None

    async def aexport(self, realm: str | None = None, *, alias: str, format: str | None = None) -> str | None:
        """Export identity provider configuration (async).
        
        Args:
            realm: The realm name
            alias: Identity provider alias
            format: Export format (e.g., 'json', 'saml-metadata')
            
        Returns:
            Exported configuration in requested format
        """
        response = await self._async_detailed(
            get_admin_realms_realm_identity_provider_instances_alias_export.asyncio_detailed,
            realm,
            alias=alias,
            format_=format,
        )
        if response.status_code == 200:
            return response.content.decode('utf-8') if response.content else None
        return None

    def import_config(self, realm: str | None = None, *, data: dict) -> dict[str, str] | None:
        """Import identity provider from configuration (sync).
        
        Args:
            realm: The realm name
            data: Identity provider configuration to import
            
        Returns:
            Import result with created provider details
        """
        return self._sync_ap(
            post_admin_realms_realm_identity_provider_import_config.sync,
            realm,
            body=data
        )

    async def aimport_config(self, realm: str | None = None, *, data: dict) -> dict[str, str] | None:
        """Import identity provider from configuration (async).
        
        Args:
            realm: The realm name
            data: Identity provider configuration to import
            
        Returns:
            Import result with created provider details
        """
        return await self._async_ap(
            post_admin_realms_realm_identity_provider_import_config.asyncio,
            realm,
            body=data
        )


class IdentityProvidersClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the IdentityProvidersAPI.
    """

    @cached_property
    def identity_providers(self) -> IdentityProvidersAPI:
        """Get the IdentityProvidersAPI instance."""
        return IdentityProvidersAPI(manager=self)  # type: ignore[arg-type]
