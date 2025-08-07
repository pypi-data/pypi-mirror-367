"""Protocol mapper management API methods."""
from functools import cached_property

from .base import BaseAPI
from ..generated.api.protocol_mappers import (
    # Client protocol mappers
    get_admin_realms_realm_clients_client_uuid_protocol_mappers_models,
    post_admin_realms_realm_clients_client_uuid_protocol_mappers_models,
    get_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id,
    put_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id,
    delete_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id,
    get_admin_realms_realm_clients_client_uuid_protocol_mappers_protocol_protocol,
    post_admin_realms_realm_clients_client_uuid_protocol_mappers_add_models,
    # Client scope protocol mappers
    get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models,
    post_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models,
    get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id,
    put_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id,
    delete_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id,
    get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_protocol_protocol,
    post_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_add_models,
)
from ..generated.models import ProtocolMapperRepresentation
from ..exceptions import APIError

__all__ = "ProtocolMappersAPI", "ProtocolMappersClientMixin", "ProtocolMapperRepresentation"


class ProtocolMappersAPI(BaseAPI):
    """Protocol mapper management API methods."""

    # Client Protocol Mappers
    def get_client_mappers(self, realm: str | None = None, *, client_uuid: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client (sync).
        
        Protocol mappers transform user data and attributes into tokens.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of protocol mappers configured for the client
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_protocol_mappers_models.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_client_mappers(self, realm: str | None = None, *, client_uuid: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client (async).
        
        Protocol mappers transform user data and attributes into tokens.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of protocol mappers configured for the client
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_protocol_mappers_models.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def create_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Create a protocol mapper for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_data: Protocol mapper configuration
            
        Raises:
            APIError: If mapper creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_protocol_mappers_models.sync_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client mapper: {response.status_code}")

    async def acreate_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Create a protocol mapper for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_data: Protocol mapper configuration
            
        Raises:
            APIError: If mapper creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_protocol_mappers_models.asyncio_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create client mapper: {response.status_code}")

    def get_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_id: str) -> ProtocolMapperRepresentation | None:
        """Get a protocol mapper for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_id: Protocol mapper ID
            
        Returns:
            Protocol mapper configuration
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id.sync,
            realm,
            client_uuid=client_uuid,
            id=mapper_id
        )

    async def aget_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_id: str) -> ProtocolMapperRepresentation | None:
        """Get a protocol mapper for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_id: Protocol mapper ID
            
        Returns:
            Protocol mapper configuration
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id.asyncio,
            realm,
            client_uuid=client_uuid,
            id=mapper_id
        )

    def update_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_id: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Update a protocol mapper for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_id: Protocol mapper ID to update
            mapper_data: Updated mapper configuration
            
        Raises:
            APIError: If mapper update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id.sync_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_uuid=client_uuid,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client mapper: {response.status_code}")

    async def aupdate_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_id: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Update a protocol mapper for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_id: Protocol mapper ID to update
            mapper_data: Updated mapper configuration
            
        Raises:
            APIError: If mapper update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id.asyncio_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_uuid=client_uuid,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update client mapper: {response.status_code}")

    def delete_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_id: str) -> None:
        """Delete a protocol mapper for a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_id: Protocol mapper ID to delete
            
        Raises:
            APIError: If mapper deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client mapper: {response.status_code}")

    async def adelete_client_mapper(self, realm: str | None = None, *, client_uuid: str, mapper_id: str) -> None:
        """Delete a protocol mapper for a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mapper_id: Protocol mapper ID to delete
            
        Raises:
            APIError: If mapper deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_protocol_mappers_models_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete client mapper: {response.status_code}")

    def get_client_mappers_by_protocol(self, realm: str | None = None, *, client_uuid: str, protocol: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client by protocol (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            protocol: Protocol name (e.g., 'openid-connect', 'saml')
            
        Returns:
            List of protocol mappers for the specified protocol
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_protocol_mappers_protocol_protocol.sync,
            realm,
            client_uuid=client_uuid,
            protocol=protocol
        )

    async def aget_client_mappers_by_protocol(self, realm: str | None = None, *, client_uuid: str, protocol: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client by protocol (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            protocol: Protocol name (e.g., 'openid-connect', 'saml')
            
        Returns:
            List of protocol mappers for the specified protocol
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_protocol_mappers_protocol_protocol.asyncio,
            realm,
            client_uuid=client_uuid,
            protocol=protocol
        )

    def add_multiple_client_mappers(self, realm: str | None = None, *, client_uuid: str, mappers: list[dict | ProtocolMapperRepresentation]) -> None:
        """Add multiple protocol mappers to a client (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mappers: List of protocol mapper configurations to add
            
        Raises:
            APIError: If adding mappers fails
        """
        mapper_objs = [m if isinstance(m, ProtocolMapperRepresentation) else ProtocolMapperRepresentation.from_dict(m) for m in mappers]
        response = self._sync_detailed(
            post_admin_realms_realm_clients_client_uuid_protocol_mappers_add_models.sync_detailed,
            realm,
            client_uuid=client_uuid,
            body=mapper_objs
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client mappers: {response.status_code}")

    async def aadd_multiple_client_mappers(self, realm: str | None = None, *, client_uuid: str, mappers: list[dict | ProtocolMapperRepresentation]) -> None:
        """Add multiple protocol mappers to a client (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            mappers: List of protocol mapper configurations to add
            
        Raises:
            APIError: If adding mappers fails
        """
        mapper_objs = [m if isinstance(m, ProtocolMapperRepresentation) else ProtocolMapperRepresentation.from_dict(m) for m in mappers]
        response = await self._async_detailed(
            post_admin_realms_realm_clients_client_uuid_protocol_mappers_add_models.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            body=mapper_objs
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add client mappers: {response.status_code}")

    # Client Scope Protocol Mappers
    def get_scope_mappers(self, realm: str | None = None, *, client_scope_id: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            
        Returns:
            List of protocol mappers configured for the client scope
        """
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models.sync,
            realm,
            client_scope_id=client_scope_id
        )

    async def aget_scope_mappers(self, realm: str | None = None, *, client_scope_id: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            
        Returns:
            List of protocol mappers configured for the client scope
        """
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models.asyncio,
            realm,
            client_scope_id=client_scope_id
        )

    def create_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Create a protocol mapper for a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_data: Protocol mapper configuration
            
        Raises:
            APIError: If mapper creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models.sync_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 201):
            raise APIError(f"Failed to create scope mapper: {response.status_code}")

    async def acreate_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Create a protocol mapper for a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_data: Protocol mapper configuration
            
        Raises:
            APIError: If mapper creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models.asyncio_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_scope_id=client_scope_id
        )
        if response.status_code not in (200, 201):
            raise APIError(f"Failed to create scope mapper: {response.status_code}")

    def get_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_id: str) -> ProtocolMapperRepresentation | None:
        """Get a protocol mapper for a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_id: Protocol mapper ID
            
        Returns:
            Protocol mapper configuration
        """
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id.sync,
            realm,
            client_scope_id=client_scope_id,
            id=mapper_id
        )

    async def aget_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_id: str) -> ProtocolMapperRepresentation | None:
        """Get a protocol mapper for a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_id: Protocol mapper ID
            
        Returns:
            Protocol mapper configuration
        """
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id.asyncio,
            realm,
            client_scope_id=client_scope_id,
            id=mapper_id
        )

    def update_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_id: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Update a protocol mapper for a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_id: Protocol mapper ID to update
            mapper_data: Updated mapper configuration
            
        Raises:
            APIError: If mapper update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id.sync_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_scope_id=client_scope_id,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update scope mapper: {response.status_code}")

    async def aupdate_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_id: str, mapper_data: dict | ProtocolMapperRepresentation) -> None:
        """Update a protocol mapper for a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_id: Protocol mapper ID to update
            mapper_data: Updated mapper configuration
            
        Raises:
            APIError: If mapper update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id.asyncio_detailed,
            realm,
            mapper_data,
            ProtocolMapperRepresentation,
            client_scope_id=client_scope_id,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update scope mapper: {response.status_code}")

    def delete_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_id: str) -> None:
        """Delete a protocol mapper for a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_id: Protocol mapper ID to delete
            
        Raises:
            APIError: If mapper deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete scope mapper: {response.status_code}")

    async def adelete_scope_mapper(self, realm: str | None = None, *, client_scope_id: str, mapper_id: str) -> None:
        """Delete a protocol mapper for a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mapper_id: Protocol mapper ID to delete
            
        Raises:
            APIError: If mapper deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_models_id.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
            id=mapper_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete scope mapper: {response.status_code}")

    def get_scope_mappers_by_protocol(self, realm: str | None = None, *, client_scope_id: str, protocol: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client scope by protocol (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            protocol: Protocol name (e.g., 'openid-connect', 'saml')
            
        Returns:
            List of protocol mappers for the specified protocol
        """
        return self._sync(
            get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_protocol_protocol.sync,
            realm,
            client_scope_id=client_scope_id,
            protocol=protocol
        )

    async def aget_scope_mappers_by_protocol(self, realm: str | None = None, *, client_scope_id: str, protocol: str) -> list[ProtocolMapperRepresentation] | None:
        """Get protocol mappers for a client scope by protocol (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            protocol: Protocol name (e.g., 'openid-connect', 'saml')
            
        Returns:
            List of protocol mappers for the specified protocol
        """
        return await self._async(
            get_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_protocol_protocol.asyncio,
            realm,
            client_scope_id=client_scope_id,
            protocol=protocol
        )

    def add_multiple_scope_mappers(self, realm: str | None = None, *, client_scope_id: str, mappers: list[dict | ProtocolMapperRepresentation]) -> None:
        """Add multiple protocol mappers to a client scope (sync).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mappers: List of protocol mapper configurations to add
            
        Raises:
            APIError: If adding mappers fails
        """
        mapper_objs = [m if isinstance(m, ProtocolMapperRepresentation) else ProtocolMapperRepresentation.from_dict(m) for m in mappers]
        response = self._sync_detailed(
            post_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_add_models.sync_detailed,
            realm,
            client_scope_id=client_scope_id,
            body=mapper_objs
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add scope mappers: {response.status_code}")

    async def aadd_multiple_scope_mappers(self, realm: str | None = None, *, client_scope_id: str, mappers: list[dict | ProtocolMapperRepresentation]) -> None:
        """Add multiple protocol mappers to a client scope (async).
        
        Args:
            realm: The realm name
            client_scope_id: Client scope ID
            mappers: List of protocol mapper configurations to add
            
        Raises:
            APIError: If adding mappers fails
        """
        mapper_objs = [m if isinstance(m, ProtocolMapperRepresentation) else ProtocolMapperRepresentation.from_dict(m) for m in mappers]
        response = await self._async_detailed(
            post_admin_realms_realm_client_scopes_client_scope_id_protocol_mappers_add_models.asyncio_detailed,
            realm,
            client_scope_id=client_scope_id,
            body=mapper_objs
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to add scope mappers: {response.status_code}")


class ProtocolMappersClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ProtocolMappersAPI.
    """

    @cached_property
    def protocol_mappers(self) -> ProtocolMappersAPI:
        """Get the ProtocolMappersAPI instance."""
        return ProtocolMappersAPI(manager=self)  # type: ignore[arg-type]
