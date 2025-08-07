"""Authorization management API methods."""
import json
from functools import cached_property
from typing import Any

from .base import BaseAPI
from ..generated.api.default import (
    # Resource Server
    get_admin_realms_realm_clients_client_uuid_authz_resource_server,
    put_admin_realms_realm_clients_client_uuid_authz_resource_server,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_settings,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_import,
    # Resources
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_resource,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id,
    put_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id,
    delete_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_search,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_attributes,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_permissions,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_scopes,
    # Scopes  
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_scope,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id,
    put_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id,
    delete_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_search,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id_permissions,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id_resources,
    # Policies
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_policy,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_search,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_providers,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_evaluate,
    # Permissions
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_permission,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_search,
    get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_providers,
    post_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_evaluate,
)
from ..generated.models import (
    ResourceServerRepresentation,
    ResourceRepresentation,
    ScopeRepresentation,
    AbstractPolicyRepresentation,
    PolicyProviderRepresentation,
    PolicyEvaluationResponse,
    PolicyEvaluationRequest,
    EvaluationResultRepresentation,
    PolicyRepresentation,
)
from ..generated.types import UNSET, Unset
from ..exceptions import APIError

__all__ = (
    "AuthorizationAPI",
    "AuthorizationClientMixin",
    "ResourceServerRepresentation",
    "ResourceRepresentation",
    "ScopeRepresentation",
    "AbstractPolicyRepresentation",
    "PolicyProviderRepresentation",
    "PolicyEvaluationResponse",
    "PolicyEvaluationRequest",
    "EvaluationResultRepresentation",
    "PolicyRepresentation",
)


class AuthorizationAPI(BaseAPI):
    """Authorization management API methods for resource servers, policies, permissions, and resources."""

    # Resource Server Management
    def get_resource_server(self, realm: str | None = None, *, client_uuid: str) -> ResourceServerRepresentation | None:
        """Get resource server settings (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Resource server configuration
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_resource_server(self, realm: str | None = None, *, client_uuid: str) -> ResourceServerRepresentation | None:
        """Get resource server settings (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Resource server configuration
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def update_resource_server(self, realm: str | None = None, *, client_uuid: str, server_data: dict | ResourceServerRepresentation) -> None:
        """Update resource server settings (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            server_data: Updated resource server configuration
            
        Raises:
            APIError: If update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid_authz_resource_server.sync_detailed,
            realm,
            server_data,
            ResourceServerRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update resource server: {response.status_code}")

    async def aupdate_resource_server(self, realm: str | None = None, *, client_uuid: str, server_data: dict | ResourceServerRepresentation) -> None:
        """Update resource server settings (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            server_data: Updated resource server configuration
            
        Raises:
            APIError: If update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid_authz_resource_server.asyncio_detailed,
            realm,
            server_data,
            ResourceServerRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update resource server: {response.status_code}")

    def get_resource_server_settings(self, realm: str | None = None, *, client_uuid: str) -> ResourceServerRepresentation | None:
        """Get resource server configuration settings (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Resource server settings including policies and permissions
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_settings.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_resource_server_settings(self, realm: str | None = None, *, client_uuid: str) -> ResourceServerRepresentation | None:
        """Get resource server configuration settings (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            Resource server settings including policies and permissions
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_settings.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def import_resource_server(self, realm: str | None = None, *, client_uuid: str, import_data: dict | ResourceServerRepresentation) -> None:
        """Import resource server configuration (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            import_data: Resource server configuration to import
            
        Raises:
            APIError: If import fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_import.sync_detailed,
            realm,
            import_data,
            ResourceServerRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 201, 204):
            raise APIError(f"Failed to import resource server: {response.status_code}")

    async def aimport_resource_server(self, realm: str | None = None, *, client_uuid: str, import_data: dict | ResourceServerRepresentation) -> None:
        """Import resource server configuration (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            import_data: Resource server configuration to import
            
        Raises:
            APIError: If import fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_import.asyncio_detailed,
            realm,
            import_data,
            ResourceServerRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code not in (200, 201, 204):
            raise APIError(f"Failed to import resource server: {response.status_code}")

    # Resource Management
    def get_resources(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET,
    ) -> list[ResourceRepresentation] | None:
        """Get resources.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            field_id: Filter by resource ID
            deep: Deep search
            exact_name: Exact name match
            first: Pagination offset
            matching_uri: Match by URI
            max: Maximum results to return
            name: Filter by resource name
            owner: Filter by owner
            scope: Filter by scope
            type: Filter by resource type
            uri: Filter by URI
            
        Returns:
            List of resources matching the filters
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource.sync,
            realm,
            client_uuid=client_uuid,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            name=name,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri,
        )

    async def aget_resources(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET,
    ) -> list[ResourceRepresentation] | None:
        """Get resources (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            field_id: Filter by resource ID
            deep: Deep search
            exact_name: Exact name match
            first: Pagination offset
            matching_uri: Match by URI
            max: Maximum results to return
            name: Filter by resource name
            owner: Filter by owner
            scope: Filter by scope
            type: Filter by resource type
            uri: Filter by URI
            
        Returns:
            List of resources matching the filters
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource.asyncio,
            realm,
            client_uuid=client_uuid,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            name=name,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri,
        )

    def create_resource(self, realm: str | None = None, *, client_uuid: str, resource_data: dict | ResourceRepresentation) -> ResourceRepresentation:
        """Create a resource (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_data: Resource configuration
            
        Returns:
            Created resource representation
            
        Raises:
            APIError: If resource creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_resource.sync_detailed,
            realm,
            body=resource_data,
            model_class=ResourceRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create resource: {response.status_code}")
        return response.parsed

    async def acreate_resource(self, realm: str | None = None, *, client_uuid: str, resource_data: dict | ResourceRepresentation) -> ResourceRepresentation:
        """Create a resource (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_data: Resource configuration
            
        Returns:
            Created resource representation
            
        Raises:
            APIError: If resource creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_resource.asyncio_detailed,
            realm,
            body=resource_data,
            model_class=ResourceRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create resource: {response.status_code}")
        return response.parsed

    def get_resource(self, realm: str | None = None, *, client_uuid: str, resource_id: str) -> ResourceRepresentation | None:
        """Get a resource by ID (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            
        Returns:
            Resource representation
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id.sync,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id
        )

    async def aget_resource(self, realm: str | None = None, *, client_uuid: str, resource_id: str) -> ResourceRepresentation | None:
        """Get a resource by ID (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            
        Returns:
            Resource representation
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id.asyncio,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id
        )

    def update_resource(self, realm: str | None = None, *, client_uuid: str, resource_id: str, resource_data: dict | ResourceRepresentation) -> None:
        """Update a resource (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID to update
            resource_data: Updated resource configuration
            
        Raises:
            APIError: If resource update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id.sync_detailed,
            realm,
            body=resource_data,
            model_class=ResourceRepresentation,
            client_uuid=client_uuid,
            resource_id=resource_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update resource: {response.status_code}")

    async def aupdate_resource(self, realm: str | None = None, *, client_uuid: str, resource_id: str, resource_data: dict | ResourceRepresentation) -> None:
        """Update a resource (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID to update
            resource_data: Updated resource configuration
            
        Raises:
            APIError: If resource update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id.asyncio_detailed,
            realm,
            body=resource_data,
            model_class=ResourceRepresentation,
            client_uuid=client_uuid,
            resource_id=resource_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update resource: {response.status_code}")

    def delete_resource(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        resource_id: str,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET
    ) -> None:
        """Delete a resource (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID to delete
            field_id: Filter by field ID
            deep: Deep search
            exact_name: Exact name match
            first: Pagination offset
            matching_uri: Match by URI
            max: Maximum results
            name: Filter by name
            owner: Filter by owner
            scope: Filter by scope
            type: Filter by type
            uri: Filter by URI
            
        Raises:
            APIError: If resource deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            name=name,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete resource: {response.status_code}")

    async def adelete_resource(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        resource_id: str,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET
    ) -> None:
        """Delete a resource (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID to delete
            field_id: Filter by field ID
            deep: Deep search
            exact_name: Exact name match
            first: Pagination offset
            matching_uri: Match by URI
            max: Maximum results
            name: Filter by name
            owner: Filter by owner
            scope: Filter by scope
            type: Filter by type
            uri: Filter by URI
            
        Raises:
            APIError: If resource deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            name=name,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete resource: {response.status_code}")

    def search_resources(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        name: Unset | str = UNSET,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET,
    ) -> list[ResourceRepresentation] | None:
        """Search resources.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            name: Filter by resource name
            field_id: Filter by resource ID
            deep: Deep search
            exact_name: Exact name match
            first: Pagination offset
            matching_uri: Match by URI
            max: Maximum results to return
            owner: Filter by owner
            scope: Filter by scope
            type: Filter by resource type
            uri: Filter by URI
            
        Returns:
            Resources matching the search criteria
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_search.sync,
            realm,
            client_uuid=client_uuid,
            name=name,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri,
        )

    async def asearch_resources(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        name: Unset | str = UNSET,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET,
    ) -> list[ResourceRepresentation] | None:
        """Search resources (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            name: Filter by resource name
            field_id: Filter by resource ID
            deep: Deep search
            exact_name: Exact name match
            first: Pagination offset
            matching_uri: Match by URI
            max: Maximum results to return
            owner: Filter by owner
            scope: Filter by scope
            type: Filter by resource type
            uri: Filter by URI
            
        Returns:
            Resources matching the search criteria
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_search.asyncio,
            realm,
            client_uuid=client_uuid,
            name=name,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri,
        )

    # Scope Management
    def get_scopes(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        scope_id: Unset | str = UNSET,
    ) -> list[ScopeRepresentation] | None:
        """Get scopes.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            name: Filter by scope name
            scope_id: Filter by scope ID
            
        Returns:
            List of scopes
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope.sync,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
            name=name,
            scope_id=scope_id,
        )

    async def aget_scopes(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        scope_id: Unset | str = UNSET,
    ) -> list[ScopeRepresentation] | None:
        """Get scopes (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            first: Pagination offset
            max: Maximum results to return
            name: Filter by scope name
            scope_id: Filter by scope ID
            
        Returns:
            List of scopes
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope.asyncio,
            realm,
            client_uuid=client_uuid,
            first=first,
            max_=max,
            name=name,
            scope_id=scope_id,
        )

    def create_scope(self, realm: str | None = None, *, client_uuid: str, scope_data: dict | ScopeRepresentation) -> ScopeRepresentation:
        """Create a scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_data: Scope configuration
            
        Returns:
            Created scope representation
            
        Raises:
            APIError: If scope creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_scope.sync_detailed,
            realm,
            body=scope_data,
            model_class=ScopeRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create scope: {response.status_code}")
        return response.parsed

    async def acreate_scope(self, realm: str | None = None, *, client_uuid: str, scope_data: dict | ScopeRepresentation) -> ScopeRepresentation:
        """Create a scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_data: Scope configuration
            
        Returns:
            Created scope representation
            
        Raises:
            APIError: If scope creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_scope.asyncio_detailed,
            realm,
            body=scope_data,
            model_class=ScopeRepresentation,
            client_uuid=client_uuid
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create scope: {response.status_code}")
        return response.parsed

    def get_scope(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> ScopeRepresentation | None:
        """Get a scope by ID (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID
            
        Returns:
            Scope representation
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id.sync,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id
        )

    async def aget_scope(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> ScopeRepresentation | None:
        """Get a scope by ID (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID
            
        Returns:
            Scope representation
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id.asyncio,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id
        )

    def update_scope(self, realm: str | None = None, *, client_uuid: str, scope_id: str, scope_data: dict | ScopeRepresentation) -> None:
        """Update a scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID to update
            scope_data: Updated scope configuration
            
        Raises:
            APIError: If scope update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id.sync_detailed,
            realm,
            body=scope_data,
            model_class=ScopeRepresentation,
            client_uuid=client_uuid,
            scope_id=scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update scope: {response.status_code}")

    async def aupdate_scope(self, realm: str | None = None, *, client_uuid: str, scope_id: str, scope_data: dict | ScopeRepresentation) -> None:
        """Update a scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID to update
            scope_data: Updated scope configuration
            
        Raises:
            APIError: If scope update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id.asyncio_detailed,
            realm,
            body=scope_data,
            model_class=ScopeRepresentation,
            client_uuid=client_uuid,
            scope_id=scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update scope: {response.status_code}")

    def delete_scope(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> None:
        """Delete a scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID to delete
        """
        response = self._sync(
            delete_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id.sync_detailed,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete scope: {response.status_code}")

    async def adelete_scope(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> None:
        """Delete a scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID to delete
        """
        response = await self._async(
            delete_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete scope: {response.status_code}")

    def search_scopes(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        name: Unset | str = UNSET,
    ) -> list[ScopeRepresentation] | None:
        """Search scopes.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            name: Filter by scope name
            
        Returns:
            List of scopes matching the search criteria
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_search.sync,
            realm,
            client_uuid=client_uuid,
            name=name,
        )

    async def asearch_scopes(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        name: Unset | str = UNSET,
    ) -> list[ScopeRepresentation] | None:
        """Search scopes (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            name: Filter by scope name
            
        Returns:
            List of scopes matching the search criteria
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_search.asyncio,
            realm,
            client_uuid=client_uuid,
            name=name,
        )

    # Policy Management
    def get_policies(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        permission: Unset | bool = UNSET,
        policy_id: Unset | str = UNSET,
        resource: Unset | str = UNSET,
        resource_type: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Get policies.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            first: Pagination offset
            max: Maximum results to return
            name: Filter by policy name
            owner: Filter by owner
            permission: Filter by permission
            policy_id: Filter by policy ID
            resource: Filter by resource
            resource_type: Filter by resource type
            scope: Filter by scope
            type: Filter by policy type
            
        Returns:
            List of policies
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy.sync,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            first=first,
            max_=max,
            name=name,
            owner=owner,
            permission=permission,
            policy_id=policy_id,
            resource=resource,
            resource_type=resource_type,
            scope=scope,
            type_=type,
        )

    async def aget_policies(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        permission: Unset | bool = UNSET,
        policy_id: Unset | str = UNSET,
        resource: Unset | str = UNSET,
        resource_type: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Get policies (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            first: Pagination offset
            max: Maximum results to return
            name: Filter by policy name
            owner: Filter by owner
            permission: Filter by permission
            policy_id: Filter by policy ID
            resource: Filter by resource
            resource_type: Filter by resource type
            scope: Filter by scope
            type: Filter by policy type
            
        Returns:
            List of policies
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy.asyncio,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            first=first,
            max_=max,
            name=name,
            owner=owner,
            permission=permission,
            policy_id=policy_id,
            resource=resource,
            resource_type=resource_type,
            scope=scope,
            type_=type,
        )

    def create_policy(self, realm: str | None = None, *, client_uuid: str, policy_data: dict) -> AbstractPolicyRepresentation:
        """Create a policy (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            policy_data: Policy configuration
            
        Returns:
            Created policy representation
            
        Raises:
            APIError: If policy creation fails
        """
        response = self._sync_detailed_json(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_policy.sync_detailed,
            realm,
            client_uuid=client_uuid,
            body=policy_data
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create policy: {response.status_code}")
        return response.parsed

    async def acreate_policy(self, realm: str | None = None, *, client_uuid: str, policy_data: dict) -> AbstractPolicyRepresentation:
        """Create a policy (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            policy_data: Policy configuration
            
        Returns:
            Created policy representation
            
        Raises:
            APIError: If policy creation fails
        """
        response = await self._async_detailed_json(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_policy.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            body=policy_data
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create policy: {response.status_code}")
        return response.parsed

    def search_policies(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        name: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Search policies.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            name: Filter by policy name
            
        Returns:
            List of policies matching the search criteria
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_search.sync,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            name=name,
        )

    async def asearch_policies(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        name: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Search policies (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            name: Filter by policy name
            
        Returns:
            List of policies matching the search criteria
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_search.asyncio,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            name=name,
        )

    def get_policy_providers(self, realm: str | None = None, *, client_uuid: str) -> list[PolicyProviderRepresentation] | None:
        """Get policy providers (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of available policy providers
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_providers.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_policy_providers(self, realm: str | None = None, *, client_uuid: str) -> list[PolicyProviderRepresentation] | None:
        """Get policy providers (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of available policy providers
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_providers.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def evaluate_policies(self, realm: str | None = None, *, client_uuid: str, evaluation_data: dict | PolicyEvaluationRequest) -> PolicyEvaluationResponse | None:
        """Evaluate policies (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            evaluation_data: Policy evaluation request data
            
        Returns:
            Policy evaluation results
            
        Raises:
            APIError: If policy evaluation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_evaluate.sync_detailed,
            realm,
            body=evaluation_data,
            model_class=PolicyEvaluationRequest,
            client_uuid=client_uuid
        )
        if response.status_code != 200:
            raise APIError(f"Failed to evaluate policies: {response.status_code}")
        return response.parsed

    async def aevaluate_policies(self, realm: str | None = None, *, client_uuid: str, evaluation_data: dict | PolicyEvaluationRequest) -> PolicyEvaluationResponse | None:
        """Evaluate policies (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            evaluation_data: Policy evaluation request data
            
        Returns:
            Policy evaluation results
            
        Raises:
            APIError: If policy evaluation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_policy_evaluate.asyncio_detailed,
            realm,
            body=evaluation_data,
            model_class=PolicyEvaluationRequest,
            client_uuid=client_uuid
        )
        if response.status_code != 200:
            raise APIError(f"Failed to evaluate policies: {response.status_code}")
        return response.parsed

    # Permission Management
    def get_permissions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        permission: Unset | bool = UNSET,
        policy_id: Unset | str = UNSET,
        resource: Unset | str = UNSET,
        resource_type: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Get permissions.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            first: Pagination offset
            max: Maximum results to return
            name: Filter by permission name
            owner: Filter by owner
            permission: Filter by permission
            policy_id: Filter by policy ID
            resource: Filter by resource
            resource_type: Filter by resource type
            scope: Filter by scope
            type: Filter by permission type
            
        Returns:
            List of permissions
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission.sync,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            first=first,
            max_=max,
            name=name,
            owner=owner,
            permission=permission,
            policy_id=policy_id,
            resource=resource,
            resource_type=resource_type,
            scope=scope,
            type_=type,
        )

    async def aget_permissions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        first: Unset | int = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        permission: Unset | bool = UNSET,
        policy_id: Unset | str = UNSET,
        resource: Unset | str = UNSET,
        resource_type: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Get permissions (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            first: Pagination offset
            max: Maximum results to return
            name: Filter by permission name
            owner: Filter by owner
            permission: Filter by permission
            policy_id: Filter by policy ID
            resource: Filter by resource
            resource_type: Filter by resource type
            scope: Filter by scope
            type: Filter by permission type
            
        Returns:
            List of permissions
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission.asyncio,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            first=first,
            max_=max,
            name=name,
            owner=owner,
            permission=permission,
            policy_id=policy_id,
            resource=resource,
            resource_type=resource_type,
            scope=scope,
            type_=type,
        )

    def create_permission(self, realm: str | None = None, *, client_uuid: str, permission_data: dict) -> AbstractPolicyRepresentation:
        """Create a permission (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            permission_data: Permission configuration
            
        Returns:
            Created permission representation
            
        Raises:
            APIError: If permission creation fails
        """
        response = self._sync_detailed_json(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_permission.sync_detailed,
            realm,
            client_uuid=client_uuid,
            body=permission_data
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create permission: {response.status_code}")
        return response.parsed

    async def acreate_permission(self, realm: str | None = None, *, client_uuid: str, permission_data: dict) -> AbstractPolicyRepresentation:
        """Create a permission (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            permission_data: Permission configuration
            
        Returns:
            Created permission representation
            
        Raises:
            APIError: If permission creation fails
        """
        response = await self._async_detailed_json(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_permission.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            body=permission_data
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create permission: {response.status_code}")
        return response.parsed

    def search_permissions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        name: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Search permissions.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            name: Filter by permission name
            
        Returns:
            List of permissions matching the search criteria
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_search.sync,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            name=name,
        )

    async def asearch_permissions(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        fields: Unset | str = UNSET,
        name: Unset | str = UNSET,
    ) -> list[AbstractPolicyRepresentation] | None:
        """Search permissions (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            fields: Fields to return
            name: Filter by permission name
            
        Returns:
            List of permissions matching the search criteria
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_search.asyncio,
            realm,
            client_uuid=client_uuid,
            fields=fields,
            name=name,
        )

    def get_permission_providers(self, realm: str | None = None, *, client_uuid: str) -> list[PolicyProviderRepresentation] | None:
        """Get permission providers (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of available permission providers
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_providers.sync,
            realm,
            client_uuid=client_uuid
        )

    async def aget_permission_providers(self, realm: str | None = None, *, client_uuid: str) -> list[PolicyProviderRepresentation] | None:
        """Get permission providers (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            
        Returns:
            List of available permission providers
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_providers.asyncio,
            realm,
            client_uuid=client_uuid
        )

    def evaluate_permissions(self, realm: str | None = None, *, client_uuid: str, evaluation_data: dict | PolicyEvaluationRequest) -> PolicyEvaluationResponse | None:
        """Evaluate permissions (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            evaluation_data: Permission evaluation request data
            
        Returns:
            Permission evaluation results
            
        Raises:
            APIError: If permission evaluation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_evaluate.sync_detailed,
            realm,
            body=evaluation_data,
            model_class=PolicyEvaluationRequest,
            client_uuid=client_uuid
        )
        if response.status_code != 200:
            raise APIError(f"Failed to evaluate permissions: {response.status_code}")
        return response.parsed

    async def aevaluate_permissions(self, realm: str | None = None, *, client_uuid: str, evaluation_data: dict | PolicyEvaluationRequest) -> PolicyEvaluationResponse | None:
        """Evaluate permissions (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            evaluation_data: Permission evaluation request data
            
        Returns:
            Permission evaluation results
            
        Raises:
            APIError: If permission evaluation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_authz_resource_server_permission_evaluate.asyncio_detailed,
            realm,
            body=evaluation_data,
            model_class=PolicyEvaluationRequest,
            client_uuid=client_uuid
        )
        if response.status_code != 200:
            raise APIError(f"Failed to evaluate permissions: {response.status_code}")
        return response.parsed

    # Resource additional endpoints
    def get_resource_attributes(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        resource_id: str,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET,
    ) -> dict[str, Any] | None:
        """Get resource attributes (sync).
        
        NOTE: This endpoint's OpenAPI spec is broken - it doesn't define a response schema
        and doesn't generate a sync function. The actual response needs to be manually extracted.
        TODO: Verify actual Keycloak API response format and report OpenAPI spec issue if needed.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            field_id: Field ID to filter by
            deep: Return deep representation
            exact_name: Match exact name
            first: First result to return
            matching_uri: Match by URI
            max: Maximum results to return
            name: Name to filter by
            owner: Owner to filter by
            scope: Scope to filter by
            type: Type to filter by
            uri: URI to filter by
            
        Returns:
            Resource attributes dictionary
        """
        response = self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_attributes.sync_detailed,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            name=name,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri,
        )
        if response.status_code == 200:
            return json.loads(response.content)
        return None

    async def aget_resource_attributes(
        self,
        realm: str | None = None,
        *,
        client_uuid: str,
        resource_id: str,
        field_id: Unset | str = UNSET,
        deep: Unset | bool = UNSET,
        exact_name: Unset | bool = UNSET,
        first: Unset | int = UNSET,
        matching_uri: Unset | bool = UNSET,
        max: Unset | int = UNSET,
        name: Unset | str = UNSET,
        owner: Unset | str = UNSET,
        scope: Unset | str = UNSET,
        type: Unset | str = UNSET,
        uri: Unset | str = UNSET,
    ) -> dict[str, Any] | None:
        """Get resource attributes (async).
        
        NOTE: This endpoint's OpenAPI spec is broken - it doesn't define a response schema
        and doesn't generate an asyncio function. The actual response needs to be manually extracted.
        TODO: Verify actual Keycloak API response format and report OpenAPI spec issue if needed.
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            field_id: Field ID to filter by
            deep: Return deep representation
            exact_name: Match exact name
            first: First result to return
            matching_uri: Match by URI
            max: Maximum results to return
            name: Name to filter by
            owner: Owner to filter by
            scope: Scope to filter by
            type: Type to filter by
            uri: URI to filter by
            
        Returns:
            Resource attributes dictionary
        """
        response = await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_attributes.asyncio_detailed,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
            field_id=field_id,
            deep=deep,
            exact_name=exact_name,
            first=first,
            matching_uri=matching_uri,
            max_=max,
            name=name,
            owner=owner,
            scope=scope,
            type_=type,
            uri=uri,
        )
        if response.status_code == 200:
            return json.loads(response.content)
        return None

    def get_resource_permissions(self, realm: str | None = None, *, client_uuid: str, resource_id: str) -> list[PolicyRepresentation] | None:
        """Get permissions for a resource (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            
        Returns:
            List of permissions for the resource
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_permissions.sync,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
        )

    async def aget_resource_permissions(self, realm: str | None = None, *, client_uuid: str, resource_id: str) -> list[PolicyRepresentation] | None:
        """Get permissions for a resource (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            
        Returns:
            List of permissions for the resource
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_permissions.asyncio,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
        )

    def get_resource_scopes(self, realm: str | None = None, *, client_uuid: str, resource_id: str) -> list[ScopeRepresentation] | None:
        """Get scopes for a resource (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            
        Returns:
            List of scopes for the resource
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_scopes.sync,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
        )

    async def aget_resource_scopes(self, realm: str | None = None, *, client_uuid: str, resource_id: str) -> list[ScopeRepresentation] | None:
        """Get scopes for a resource (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            resource_id: Resource ID
            
        Returns:
            List of scopes for the resource
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_resource_resource_id_scopes.asyncio,
            realm,
            client_uuid=client_uuid,
            resource_id=resource_id,
        )

    # Scope additional endpoints
    def get_scope_permissions(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> list[PolicyRepresentation] | None:
        """Get permissions for a scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID
            
        Returns:
            List of permissions for the scope
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id_permissions.sync,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id,
        )

    async def aget_scope_permissions(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> list[PolicyRepresentation] | None:
        """Get permissions for a scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID
            
        Returns:
            List of permissions for the scope
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id_permissions.asyncio,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id,
        )

    def get_scope_resources(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> list[ResourceRepresentation] | None:
        """Get resources for a scope (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID
            
        Returns:
            List of resources for the scope
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id_resources.sync,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id,
        )

    async def aget_scope_resources(self, realm: str | None = None, *, client_uuid: str, scope_id: str) -> list[ResourceRepresentation] | None:
        """Get resources for a scope (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            scope_id: Scope ID
            
        Returns:
            List of resources for the scope
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_authz_resource_server_scope_scope_id_resources.asyncio,
            realm,
            client_uuid=client_uuid,
            scope_id=scope_id,
        )


class AuthorizationClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the AuthorizationAPI.
    """

    @cached_property
    def authorization(self) -> AuthorizationAPI:
        """Get the AuthorizationAPI instance."""
        return AuthorizationAPI(manager=self)  # type: ignore[arg-type]
