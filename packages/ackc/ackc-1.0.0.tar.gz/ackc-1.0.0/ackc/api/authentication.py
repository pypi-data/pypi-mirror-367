"""Authentication management API methods."""
from functools import cached_property
from typing import Any

from .base import BaseAPI
from ..generated.api.authentication_management import (
    # Flows
    get_admin_realms_realm_authentication_flows,
    post_admin_realms_realm_authentication_flows,
    get_admin_realms_realm_authentication_flows_id,
    put_admin_realms_realm_authentication_flows_id,
    delete_admin_realms_realm_authentication_flows_id,
    post_admin_realms_realm_authentication_flows_flow_alias_copy,
    # Executions
    get_admin_realms_realm_authentication_flows_flow_alias_executions,
    put_admin_realms_realm_authentication_flows_flow_alias_executions,
    post_admin_realms_realm_authentication_flows_flow_alias_executions_execution,
    post_admin_realms_realm_authentication_flows_flow_alias_executions_flow,
    get_admin_realms_realm_authentication_executions_execution_id,
    delete_admin_realms_realm_authentication_executions_execution_id,
    post_admin_realms_realm_authentication_executions_execution_id_config,
    post_admin_realms_realm_authentication_executions_execution_id_lower_priority,
    post_admin_realms_realm_authentication_executions_execution_id_raise_priority,
    get_admin_realms_realm_authentication_executions_execution_id_config_id,
    post_admin_realms_realm_authentication_executions,
    # Configs
    get_admin_realms_realm_authentication_config_id,
    put_admin_realms_realm_authentication_config_id,
    delete_admin_realms_realm_authentication_config_id,
    post_admin_realms_realm_authentication_config,
    # Providers
    get_admin_realms_realm_authentication_authenticator_providers,
    get_admin_realms_realm_authentication_client_authenticator_providers,
    get_admin_realms_realm_authentication_form_action_providers,
    get_admin_realms_realm_authentication_form_providers,
    # Required Actions
    get_admin_realms_realm_authentication_required_actions,
    get_admin_realms_realm_authentication_required_actions_alias,
    put_admin_realms_realm_authentication_required_actions_alias,
    delete_admin_realms_realm_authentication_required_actions_alias,
    post_admin_realms_realm_authentication_required_actions_alias_lower_priority,
    post_admin_realms_realm_authentication_required_actions_alias_raise_priority,
    get_admin_realms_realm_authentication_unregistered_required_actions,
    post_admin_realms_realm_authentication_register_required_action,
    get_admin_realms_realm_authentication_required_actions_alias_config,
    put_admin_realms_realm_authentication_required_actions_alias_config,
    delete_admin_realms_realm_authentication_required_actions_alias_config,
    get_admin_realms_realm_authentication_required_actions_alias_config_description,
    # Config descriptions
    get_admin_realms_realm_authentication_config_description_provider_id,
    get_admin_realms_realm_authentication_per_client_config_description,
)
from ..generated.models import (
    AuthenticationExecutionRepresentation,
    AuthenticationFlowRepresentation,
    AuthenticationExecutionInfoRepresentation,
    AuthenticatorConfigInfoRepresentation,
    AuthenticatorConfigRepresentation,
    RequiredActionConfigRepresentation,
    RequiredActionConfigInfoRepresentation,
    RequiredActionProviderRepresentation,
    PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsFlowBody,
    PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsExecutionBody,
    PostAdminRealmsRealmAuthenticationFlowsFlowAliasCopyBody,
    PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody,
)
from ..exceptions import APIError

__all__ = (
    "AuthenticationAPI", 
    "AuthenticationClientMixin",
    "AuthenticationFlowRepresentation",
    "AuthenticationExecutionRepresentation",
    "AuthenticationExecutionInfoRepresentation",
    "AuthenticatorConfigRepresentation",
    "RequiredActionProviderRepresentation",
)


class AuthenticationAPI(BaseAPI):
    """Authentication management API methods."""

    # Authentication Flows
    def get_flows(self, realm: str | None = None) -> list[AuthenticationFlowRepresentation] | None:
        """Get authentication flows (sync).
        
        Authentication flows define the sequence of authenticators for login.
        
        Args:
            realm: The realm name
            
        Returns:
            List of authentication flows configured in the realm
        """
        return self._sync(get_admin_realms_realm_authentication_flows.sync, realm)

    async def aget_flows(self, realm: str | None = None) -> list[AuthenticationFlowRepresentation] | None:
        """Get authentication flows (async).
        
        Authentication flows define the sequence of authenticators for login.
        
        Args:
            realm: The realm name
            
        Returns:
            List of authentication flows configured in the realm
        """
        return await self._async(get_admin_realms_realm_authentication_flows.asyncio, realm)

    def create_flow(self, realm: str | None = None, *, flow_data: dict | AuthenticationFlowRepresentation) -> None:
        """Create an authentication flow (sync).
        
        Args:
            realm: The realm name
            flow_data: Flow configuration including alias and provider
            
        Raises:
            APIError: If flow creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_flows.sync_detailed,
            realm,
            flow_data,
            AuthenticationFlowRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create flow: {response.status_code}")

    async def acreate_flow(self, realm: str | None = None, *, flow_data: dict | AuthenticationFlowRepresentation) -> None:
        """Create an authentication flow (async).
        
        Args:
            realm: The realm name
            flow_data: Flow configuration including alias and provider
            
        Raises:
            APIError: If flow creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_flows.asyncio_detailed,
            realm,
            flow_data,
            AuthenticationFlowRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create flow: {response.status_code}")

    def get_flow(self, realm: str | None = None, *, flow_id: str) -> AuthenticationFlowRepresentation | None:
        """Get an authentication flow by ID (sync).
        
        Args:
            realm: The realm name
            flow_id: Flow ID
            
        Returns:
            Authentication flow representation with full details
        """
        return self._sync(
            get_admin_realms_realm_authentication_flows_id.sync,
            realm,
            id=flow_id
        )

    async def aget_flow(self, realm: str | None = None, *, flow_id: str) -> AuthenticationFlowRepresentation | None:
        """Get an authentication flow by ID (async).
        
        Args:
            realm: The realm name
            flow_id: Flow ID
            
        Returns:
            Authentication flow representation with full details
        """
        return await self._async(
            get_admin_realms_realm_authentication_flows_id.asyncio,
            realm,
            id=flow_id
        )

    def update_flow(self, realm: str | None = None, *, flow_id: str, flow_data: dict | AuthenticationFlowRepresentation) -> None:
        """Update an authentication flow (sync).
        
        Args:
            realm: The realm name
            flow_id: Flow ID to update
            flow_data: Updated flow configuration
            
        Raises:
            APIError: If flow update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_authentication_flows_id.sync_detailed,
            realm,
            flow_data,
            AuthenticationFlowRepresentation,
            id=flow_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update flow: {response.status_code}")

    async def aupdate_flow(self, realm: str | None = None, *, flow_id: str, flow_data: dict | AuthenticationFlowRepresentation) -> None:
        """Update an authentication flow (async).
        
        Args:
            realm: The realm name
            flow_id: Flow ID to update
            flow_data: Updated flow configuration
            
        Raises:
            APIError: If flow update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_authentication_flows_id.asyncio_detailed,
            realm,
            flow_data,
            AuthenticationFlowRepresentation,
            id=flow_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update flow: {response.status_code}")

    def delete_flow(self, realm: str | None = None, *, flow_id: str) -> None:
        """Delete an authentication flow (sync).
        
        Args:
            realm: The realm name
            flow_id: Flow ID to delete
            
        Raises:
            APIError: If flow deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_authentication_flows_id.sync_detailed,
            realm,
            id=flow_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete flow: {response.status_code}")

    async def adelete_flow(self, realm: str | None = None, *, flow_id: str) -> None:
        """Delete an authentication flow (async).
        
        Args:
            realm: The realm name
            flow_id: Flow ID to delete
            
        Raises:
            APIError: If flow deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_authentication_flows_id.asyncio_detailed,
            realm,
            id=flow_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete flow: {response.status_code}")

    def copy_flow(self, realm: str | None = None, *, flow_alias: str, new_name: str) -> None:
        """Copy an authentication flow (sync).
        
        Args:
            realm: The realm name
            flow_alias: Alias of the flow to copy
            new_name: Name for the new flow copy
            
        Raises:
            APIError: If flow copy fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_flows_flow_alias_copy.sync_detailed,
            realm,
            {"newName": new_name},
            PostAdminRealmsRealmAuthenticationFlowsFlowAliasCopyBody,
            flow_alias=flow_alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to copy flow: {response.status_code}")

    async def acopy_flow(self, realm: str | None = None, *, flow_alias: str, new_name: str) -> None:
        """Copy an authentication flow (async).
        
        Args:
            realm: The realm name
            flow_alias: Alias of the flow to copy
            new_name: Name for the new flow copy
            
        Raises:
            APIError: If flow copy fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_flows_flow_alias_copy.asyncio_detailed,
            realm,
            {"newName": new_name},
            PostAdminRealmsRealmAuthenticationFlowsFlowAliasCopyBody,
            flow_alias=flow_alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to copy flow: {response.status_code}")

    # Flow Executions
    def get_executions(self, realm: str | None = None, *, flow_alias: str) -> list[AuthenticationExecutionInfoRepresentation] | None:
        """Get executions for a flow (sync).
        
        Args:
            realm: The realm name
            flow_alias: Flow alias
            
        Returns:
            List of authentication executions in the flow
        """
        return self._sync(
            get_admin_realms_realm_authentication_flows_flow_alias_executions.sync,
            realm,
            flow_alias=flow_alias
        )

    async def aget_executions(self, realm: str | None = None, *, flow_alias: str) -> list[AuthenticationExecutionInfoRepresentation] | None:
        """Get executions for a flow (async).
        
        Args:
            realm: The realm name
            flow_alias: Flow alias
            
        Returns:
            List of authentication executions in the flow
        """
        return await self._async(
            get_admin_realms_realm_authentication_flows_flow_alias_executions.asyncio,
            realm,
            flow_alias=flow_alias
        )

    def update_executions(self, realm: str | None = None, *, flow_alias: str, execution_data: dict | AuthenticationExecutionInfoRepresentation) -> None:
        """Update executions for a flow (sync).
        
        Args:
            realm: The realm name
            flow_alias: Flow alias
            execution_data: Updated execution configuration
            
        Raises:
            APIError: If execution update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_authentication_flows_flow_alias_executions.sync_detailed,
            realm,
            execution_data,
            AuthenticationExecutionInfoRepresentation,
            flow_alias=flow_alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update executions: {response.status_code}")

    async def aupdate_executions(self, realm: str | None = None, *, flow_alias: str, execution_data: dict | AuthenticationExecutionInfoRepresentation) -> None:
        """Update executions for a flow (async).
        
        Args:
            realm: The realm name
            flow_alias: Flow alias
            execution_data: Updated execution configuration
            
        Raises:
            APIError: If execution update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_authentication_flows_flow_alias_executions.asyncio_detailed,
            realm,
            execution_data,
            AuthenticationExecutionInfoRepresentation,
            flow_alias=flow_alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update executions: {response.status_code}")

    # Authenticator Config
    def get_config(self, realm: str | None = None, *, config_id: str) -> AuthenticatorConfigRepresentation | None:
        """Get authenticator configuration (sync).
        
        Args:
            realm: The realm name
            config_id: Configuration ID
            
        Returns:
            Authenticator configuration representation
        """
        return self._sync(
            get_admin_realms_realm_authentication_config_id.sync,
            realm,
            id=config_id
        )

    async def aget_config(self, realm: str | None = None, *, config_id: str) -> AuthenticatorConfigRepresentation | None:
        """Get authenticator configuration (async).
        
        Args:
            realm: The realm name
            config_id: Configuration ID
            
        Returns:
            Authenticator configuration representation
        """
        return await self._async(
            get_admin_realms_realm_authentication_config_id.asyncio,
            realm,
            id=config_id
        )

    def create_config(self, realm: str | None = None, *, config_data: dict | AuthenticatorConfigRepresentation) -> str:
        """Create authenticator configuration (sync).
        
        Args:
            realm: The realm name
            config_data: Authenticator configuration data
            
        Returns:
            Created configuration ID
            
        Raises:
            APIError: If configuration creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_config.sync_detailed,
            realm,
            config_data,
            AuthenticatorConfigRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create config: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    async def acreate_config(self, realm: str | None = None, *, config_data: dict | AuthenticatorConfigRepresentation) -> str:
        """Create authenticator configuration (async).
        
        Args:
            realm: The realm name
            config_data: Authenticator configuration data
            
        Returns:
            Created configuration ID
            
        Raises:
            APIError: If configuration creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_config.asyncio_detailed,
            realm,
            config_data,
            AuthenticatorConfigRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create config: {response.status_code}")
        location = response.headers.get("Location", "")
        return location.split("/")[-1] if location else ""

    def update_config(self, realm: str | None = None, *, config_id: str, config_data: dict | AuthenticatorConfigRepresentation) -> None:
        """Update authenticator configuration (sync).
        
        Args:
            realm: The realm name
            config_id: Configuration ID to update
            config_data: Updated configuration data
            
        Raises:
            APIError: If configuration update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_authentication_config_id.sync_detailed,
            realm,
            config_data,
            AuthenticatorConfigRepresentation,
            id=config_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update config: {response.status_code}")

    async def aupdate_config(self, realm: str | None = None, *, config_id: str, config_data: dict | AuthenticatorConfigRepresentation) -> None:
        """Update authenticator configuration (async).
        
        Args:
            realm: The realm name
            config_id: Configuration ID to update
            config_data: Updated configuration data
            
        Raises:
            APIError: If configuration update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_authentication_config_id.asyncio_detailed,
            realm,
            config_data,
            AuthenticatorConfigRepresentation,
            id=config_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update config: {response.status_code}")

    def delete_config(self, realm: str | None = None, *, config_id: str) -> None:
        """Delete authenticator configuration (sync).
        
        Args:
            realm: The realm name
            config_id: Configuration ID to delete
            
        Raises:
            APIError: If configuration deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_authentication_config_id.sync_detailed,
            realm,
            id=config_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete config: {response.status_code}")

    async def adelete_config(self, realm: str | None = None, *, config_id: str) -> None:
        """Delete authenticator configuration (async).
        
        Args:
            realm: The realm name
            config_id: Configuration ID to delete
            
        Raises:
            APIError: If configuration deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_authentication_config_id.asyncio_detailed,
            realm,
            id=config_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete config: {response.status_code}")

    # Providers
    def get_authenticator_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get authenticator providers (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available authenticator providers
        """
        return self._sync_ap_list(
            get_admin_realms_realm_authentication_authenticator_providers.sync,
            realm
        )

    async def aget_authenticator_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get authenticator providers (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available authenticator providers
        """
        return await self._async_ap_list(
            get_admin_realms_realm_authentication_authenticator_providers.asyncio,
            realm
        )

    def get_client_authenticator_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get client authenticator providers (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available client authenticator providers
        """
        return self._sync_ap_list(
            get_admin_realms_realm_authentication_client_authenticator_providers.sync,
            realm
        )

    async def aget_client_authenticator_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get client authenticator providers (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available client authenticator providers
        """
        return await self._async_ap_list(
            get_admin_realms_realm_authentication_client_authenticator_providers.asyncio,
            realm
        )

    def get_form_action_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get form action providers (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available form action providers
        """
        return self._sync_ap_list(
            get_admin_realms_realm_authentication_form_action_providers.sync,
            realm
        )

    async def aget_form_action_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get form action providers (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available form action providers
        """
        return await self._async_ap_list(
            get_admin_realms_realm_authentication_form_action_providers.asyncio,
            realm
        )

    def get_form_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get form providers (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available form providers
        """
        return self._sync_ap_list(
            get_admin_realms_realm_authentication_form_providers.sync,
            realm
        )

    async def aget_form_providers(self, realm: str | None = None) -> list[dict[str, Any]] | None:
        """Get form providers (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available form providers
        """
        return await self._async_ap_list(
            get_admin_realms_realm_authentication_form_providers.asyncio,
            realm
        )

    # Required Actions
    def get_required_actions(self, realm: str | None = None) -> list[RequiredActionProviderRepresentation] | None:
        """Get required actions (sync).
        
        Required actions are actions users must complete before accessing resources.
        
        Args:
            realm: The realm name
            
        Returns:
            List of required action providers
        """
        return self._sync(
            get_admin_realms_realm_authentication_required_actions.sync,
            realm
        )

    async def aget_required_actions(self, realm: str | None = None) -> list[RequiredActionProviderRepresentation] | None:
        """Get required actions (async).
        
        Required actions are actions users must complete before accessing resources.
        
        Args:
            realm: The realm name
            
        Returns:
            List of required action providers
        """
        return await self._async(
            get_admin_realms_realm_authentication_required_actions.asyncio,
            realm
        )

    def get_required_action(self, realm: str | None = None, *, alias: str) -> RequiredActionProviderRepresentation | None:
        """Get a required action by alias (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Returns:
            Required action provider representation
        """
        return self._sync(
            get_admin_realms_realm_authentication_required_actions_alias.sync,
            realm,
            alias=alias
        )

    async def aget_required_action(self, realm: str | None = None, *, alias: str) -> RequiredActionProviderRepresentation | None:
        """Get a required action by alias (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Returns:
            Required action provider representation
        """
        return await self._async(
            get_admin_realms_realm_authentication_required_actions_alias.asyncio,
            realm,
            alias=alias
        )

    def update_required_action(self, realm: str | None = None, *, alias: str, action_data: dict | RequiredActionProviderRepresentation) -> None:
        """Update a required action (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            action_data: Updated action configuration
            
        Raises:
            APIError: If update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_authentication_required_actions_alias.sync_detailed,
            realm,
            action_data,
            RequiredActionProviderRepresentation,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update required action: {response.status_code}")

    async def aupdate_required_action(self, realm: str | None = None, *, alias: str, action_data: dict | RequiredActionProviderRepresentation) -> None:
        """Update a required action (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            action_data: Updated action configuration
            
        Raises:
            APIError: If update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_authentication_required_actions_alias.asyncio_detailed,
            realm,
            action_data,
            RequiredActionProviderRepresentation,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update required action: {response.status_code}")

    def delete_required_action(self, realm: str | None = None, *, alias: str) -> None:
        """Delete a required action (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_authentication_required_actions_alias.sync_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete required action: {response.status_code}")

    async def adelete_required_action(self, realm: str | None = None, *, alias: str) -> None:
        """Delete a required action (async).
        
        Args:
            realm: The realm name
            alias: Required action alias to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_authentication_required_actions_alias.asyncio_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete required action: {response.status_code}")

    def get_unregistered_required_actions(self, realm: str | None = None) -> list[dict[str, str]] | None:
        """Get unregistered required actions (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available but unregistered required actions
        """
        return self._sync_ap_list(
            get_admin_realms_realm_authentication_unregistered_required_actions.sync,
            realm
        )

    async def aget_unregistered_required_actions(self, realm: str | None = None) -> list[dict[str, str]] | None:
        """Get unregistered required actions (async).
        
        Args:
            realm: The realm name
            
        Returns:
            List of available but unregistered required actions
        """
        return await self._async_ap_list(
            get_admin_realms_realm_authentication_unregistered_required_actions.asyncio,
            realm
        )

    def register_required_action(self, realm: str | None = None, *, provider_data: dict | PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody) -> None:
        """Register a required action (sync).
        
        Args:
            realm: The realm name
            provider_data: Provider configuration to register
            
        Raises:
            APIError: If registration fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_register_required_action.sync_detailed,
            realm,
            provider_data,
            PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody
        )
        if response.status_code != 201:
            raise APIError(f"Failed to register required action: {response.status_code}")

    async def aregister_required_action(self, realm: str | None = None, *, provider_data: dict | PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody) -> None:
        """Register a required action (async).
        
        Args:
            realm: The realm name
            provider_data: Provider configuration to register
            
        Raises:
            APIError: If registration fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_register_required_action.asyncio_detailed,
            realm,
            provider_data,
            PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody
        )
        if response.status_code != 201:
            raise APIError(f"Failed to register required action: {response.status_code}")

    def lower_required_action_priority(self, realm: str | None = None, *, alias: str) -> None:
        """Lower required action priority (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Raises:
            APIError: If priority change fails
        """
        response = self._sync(
            post_admin_realms_realm_authentication_required_actions_alias_lower_priority.sync_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to lower required action priority: {response.status_code}")

    async def alower_required_action_priority(self, realm: str | None = None, *, alias: str) -> None:
        """Lower required action priority (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Raises:
            APIError: If priority change fails
        """
        response = await self._async(
            post_admin_realms_realm_authentication_required_actions_alias_lower_priority.asyncio_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to lower required action priority: {response.status_code}")

    def raise_required_action_priority(self, realm: str | None = None, *, alias: str) -> None:
        """Raise required action priority (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Raises:
            APIError: If priority change fails
        """
        response = self._sync(
            post_admin_realms_realm_authentication_required_actions_alias_raise_priority.sync_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to raise required action priority: {response.status_code}")

    async def araise_required_action_priority(self, realm: str | None = None, *, alias: str) -> None:
        """Raise required action priority (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Raises:
            APIError: If priority change fails
        """
        response = await self._async(
            post_admin_realms_realm_authentication_required_actions_alias_raise_priority.asyncio_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to raise required action priority: {response.status_code}")

    # Execution management
    def add_execution(self, realm: str | None = None, *, flow_alias: str, provider: str) -> None:
        """Add new authentication execution (sync).
        
        Args:
            realm: The realm name
            flow_alias: Flow alias to add execution to
            provider: Provider ID for the execution
            
        Raises:
            APIError: If adding execution fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_flows_flow_alias_executions_execution.sync_detailed,
            realm,
            {"provider": provider},
            PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsExecutionBody,
            flow_alias=flow_alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to add execution: {response.status_code}")

    async def aadd_execution(self, realm: str | None = None, *, flow_alias: str, provider: str) -> None:
        """Add new authentication execution (async).
        
        Args:
            realm: The realm name
            flow_alias: Flow alias to add execution to
            provider: Provider ID for the execution
            
        Raises:
            APIError: If adding execution fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_flows_flow_alias_executions_execution.asyncio_detailed,
            realm,
            {"provider": provider},
            PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsExecutionBody,
            flow_alias=flow_alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to add execution: {response.status_code}")

    def add_flow_execution(self, realm: str | None = None, *, flow_alias: str, flow_data: dict) -> None:
        """Add new flow to execution (sync).
        
        Args:
            realm: The realm name
            flow_alias: Parent flow alias
            flow_data: Sub-flow configuration
            
        Raises:
            APIError: If adding flow execution fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_flows_flow_alias_executions_flow.sync_detailed,
            realm,
            flow_data,
            PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsFlowBody,
            flow_alias=flow_alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to add flow execution: {response.status_code}")

    async def aadd_flow_execution(self, realm: str | None = None, *, flow_alias: str, flow_data: dict) -> None:
        """Add new flow to execution (async).
        
        Args:
            realm: The realm name
            flow_alias: Parent flow alias
            flow_data: Sub-flow configuration
            
        Raises:
            APIError: If adding flow execution fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_flows_flow_alias_executions_flow.asyncio_detailed,
            realm,
            flow_data,
            PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsFlowBody,
            flow_alias=flow_alias
        )
        if response.status_code != 201:
            raise APIError(f"Failed to add flow execution: {response.status_code}")

    def get_execution(self, realm: str | None = None, *, execution_id: str) -> AuthenticationExecutionRepresentation | None:
        """Get execution by ID (sync).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            
        Returns:
            Execution configuration
        """
        return self._sync(
            get_admin_realms_realm_authentication_executions_execution_id.sync,
            realm,
            execution_id=execution_id
        )

    async def aget_execution(self, realm: str | None = None, *, execution_id: str) -> AuthenticationExecutionRepresentation | None:
        """Get execution by ID (async).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            
        Returns:
            Execution configuration
        """
        return await self._async(
            get_admin_realms_realm_authentication_executions_execution_id.asyncio,
            realm,
            execution_id=execution_id
        )

    def delete_execution(self, realm: str | None = None, *, execution_id: str) -> None:
        """Delete execution (sync).
        
        Args:
            realm: The realm name
            execution_id: Execution ID to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_authentication_executions_execution_id.sync_detailed,
            realm,
            execution_id=execution_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete execution: {response.status_code}")

    async def adelete_execution(self, realm: str | None = None, *, execution_id: str) -> None:
        """Delete execution (async).
        
        Args:
            realm: The realm name
            execution_id: Execution ID to delete
            
        Raises:
            APIError: If deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_authentication_executions_execution_id.asyncio_detailed,
            realm,
            execution_id=execution_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete execution: {response.status_code}")

    def create_execution_config(self, realm: str | None = None, *, execution_id: str, config_data: dict | AuthenticatorConfigRepresentation) -> None:
        """Create execution configuration (sync).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            config_data: Configuration data for execution
            
        Raises:
            APIError: If configuration creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_executions_execution_id_config.sync_detailed,
            realm,
            config_data,
            AuthenticatorConfigRepresentation,
            execution_id=execution_id
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create execution config: {response.status_code}")

    async def acreate_execution_config(self, realm: str | None = None, *, execution_id: str, config_data: dict | AuthenticatorConfigRepresentation) -> None:
        """Create execution configuration (async).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            config_data: Configuration data for execution
            
        Raises:
            APIError: If configuration creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_executions_execution_id_config.asyncio_detailed,
            realm,
            config_data,
            AuthenticatorConfigRepresentation,
            execution_id=execution_id
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create execution config: {response.status_code}")

    def lower_execution_priority(self, realm: str | None = None, *, execution_id: str) -> None:
        """Lower execution priority (sync).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            
        Raises:
            APIError: If priority change fails
        """
        response = self._sync(
            post_admin_realms_realm_authentication_executions_execution_id_lower_priority.sync_detailed,
            realm,
            execution_id=execution_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to lower execution priority: {response.status_code}")

    async def alower_execution_priority(self, realm: str | None = None, *, execution_id: str) -> None:
        """Lower execution priority (async).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            
        Raises:
            APIError: If priority change fails
        """
        response = await self._async(
            post_admin_realms_realm_authentication_executions_execution_id_lower_priority.asyncio_detailed,
            realm,
            execution_id=execution_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to lower execution priority: {response.status_code}")

    def raise_execution_priority(self, realm: str | None = None, *, execution_id: str) -> None:
        """Raise execution priority (sync).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            
        Raises:
            APIError: If priority change fails
        """
        response = self._sync(
            post_admin_realms_realm_authentication_executions_execution_id_raise_priority.sync_detailed,
            realm,
            execution_id=execution_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to raise execution priority: {response.status_code}")

    async def araise_execution_priority(self, realm: str | None = None, *, execution_id: str) -> None:
        """Raise execution priority (async).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            
        Raises:
            APIError: If priority change fails
        """
        response = await self._async(
            post_admin_realms_realm_authentication_executions_execution_id_raise_priority.asyncio_detailed,
            realm,
            execution_id=execution_id
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to raise execution priority: {response.status_code}")

    def get_execution_config(self, realm: str | None = None, *, execution_id: str, config_id: str) -> AuthenticatorConfigRepresentation | None:
        """Get execution configuration by ID (sync).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            config_id: Configuration ID
            
        Returns:
            Execution configuration
        """
        return self._sync(
            get_admin_realms_realm_authentication_executions_execution_id_config_id.sync,
            realm,
            execution_id=execution_id,
            id=config_id
        )

    async def aget_execution_config(self, realm: str | None = None, *, execution_id: str, config_id: str) -> AuthenticatorConfigRepresentation | None:
        """Get execution configuration by ID (async).
        
        Args:
            realm: The realm name
            execution_id: Execution ID
            config_id: Configuration ID
            
        Returns:
            Execution configuration
        """
        return await self._async(
            get_admin_realms_realm_authentication_executions_execution_id_config_id.asyncio,
            realm,
            execution_id=execution_id,
            id=config_id
        )

    def create_execution(self, realm: str | None = None, *, execution_data: dict | AuthenticationExecutionRepresentation) -> None:
        """Create authentication execution (sync).
        
        Args:
            realm: The realm name
            execution_data: Execution configuration
            
        Raises:
            APIError: If execution creation fails
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_authentication_executions.sync_detailed,
            realm,
            execution_data,
            AuthenticationExecutionRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create execution: {response.status_code}")

    async def acreate_execution(self, realm: str | None = None, *, execution_data: dict | AuthenticationExecutionRepresentation) -> None:
        """Create authentication execution (async).
        
        Args:
            realm: The realm name
            execution_data: Execution configuration
            
        Raises:
            APIError: If execution creation fails
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_authentication_executions.asyncio_detailed,
            realm,
            execution_data,
            AuthenticationExecutionRepresentation
        )
        if response.status_code != 201:
            raise APIError(f"Failed to create execution: {response.status_code}")

    def get_required_action_config(self, realm: str | None = None, *, alias: str) -> RequiredActionConfigRepresentation | None:
        """Get required action configuration (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Returns:
            Required action configuration
        """
        return self._sync(
            get_admin_realms_realm_authentication_required_actions_alias_config.sync,
            realm,
            alias=alias
        )

    async def aget_required_action_config(self, realm: str | None = None, *, alias: str) -> RequiredActionConfigRepresentation | None:
        """Get required action configuration (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Returns:
            Required action configuration
        """
        return await self._async(
            get_admin_realms_realm_authentication_required_actions_alias_config.asyncio,
            realm,
            alias=alias
        )

    def update_required_action_config(self, realm: str | None = None, *, alias: str, config_data: dict | RequiredActionConfigRepresentation) -> None:
        """Update required action configuration (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            config_data: Updated configuration
            
        Raises:
            APIError: If configuration update fails
        """
        response = self._sync_detailed_model(
            put_admin_realms_realm_authentication_required_actions_alias_config.sync_detailed,
            realm,
            config_data,
            RequiredActionConfigRepresentation,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update required action config: {response.status_code}")

    async def aupdate_required_action_config(self, realm: str | None = None, *, alias: str, config_data: dict | RequiredActionConfigRepresentation) -> None:
        """Update required action configuration (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            config_data: Updated configuration
            
        Raises:
            APIError: If configuration update fails
        """
        response = await self._async_detailed_model(
            put_admin_realms_realm_authentication_required_actions_alias_config.asyncio_detailed,
            realm,
            config_data,
            RequiredActionConfigRepresentation,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to update required action config: {response.status_code}")

    def delete_required_action_config(self, realm: str | None = None, *, alias: str) -> None:
        """Delete required action configuration (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Raises:
            APIError: If configuration deletion fails
        """
        response = self._sync(
            delete_admin_realms_realm_authentication_required_actions_alias_config.sync_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete required action config: {response.status_code}")

    async def adelete_required_action_config(self, realm: str | None = None, *, alias: str) -> None:
        """Delete required action configuration (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Raises:
            APIError: If configuration deletion fails
        """
        response = await self._async(
            delete_admin_realms_realm_authentication_required_actions_alias_config.asyncio_detailed,
            realm,
            alias=alias
        )
        if response.status_code not in (200, 204):
            raise APIError(f"Failed to delete required action config: {response.status_code}")

    def get_required_action_config_description(self, realm: str | None = None, *, alias: str) -> RequiredActionConfigInfoRepresentation | None:
        """Get required action configuration description (sync).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Returns:
            Configuration description
        """
        return self._sync(
            get_admin_realms_realm_authentication_required_actions_alias_config_description.sync,
            realm,
            alias=alias
        )

    async def aget_required_action_config_description(self, realm: str | None = None, *, alias: str) -> RequiredActionConfigInfoRepresentation | None:
        """Get required action configuration description (async).
        
        Args:
            realm: The realm name
            alias: Required action alias
            
        Returns:
            Configuration description
        """
        return await self._async(
            get_admin_realms_realm_authentication_required_actions_alias_config_description.asyncio,
            realm,
            alias=alias
        )

    def get_config_description(self, realm: str | None = None, *, provider_id: str) -> AuthenticatorConfigInfoRepresentation | None:
        """Get authenticator configuration description (sync).
        
        Args:
            realm: The realm name
            provider_id: Provider ID
            
        Returns:
            Configuration description for the provider
        """
        return self._sync(
            get_admin_realms_realm_authentication_config_description_provider_id.sync,
            realm,
            provider_id=provider_id
        )

    async def aget_config_description(self, realm: str | None = None, *, provider_id: str) -> AuthenticatorConfigInfoRepresentation | None:
        """Get authenticator configuration description (async).
        
        Args:
            realm: The realm name
            provider_id: Provider ID
            
        Returns:
            Configuration description for the provider
        """
        return await self._async(
            get_admin_realms_realm_authentication_config_description_provider_id.asyncio,
            realm,
            provider_id=provider_id
        )

    def get_per_client_config_description(self, realm: str | None = None) -> dict[str, Any] | None:
        """Get per-client configuration description (sync).
        
        Args:
            realm: The realm name
            
        Returns:
            Per-client configuration description
        """
        return self._sync_ap(
            get_admin_realms_realm_authentication_per_client_config_description.sync,
            realm
        )

    async def aget_per_client_config_description(self, realm: str | None = None) -> dict[str, Any] | None:
        """Get per-client configuration description (async).
        
        Args:
            realm: The realm name
            
        Returns:
            Per-client configuration description
        """
        return await self._async_ap(
            get_admin_realms_realm_authentication_per_client_config_description.asyncio,
            realm
        )


class AuthenticationClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the AuthenticationAPI."""

    @cached_property
    def authentication(self) -> AuthenticationAPI:
        """Get the AuthenticationAPI instance.
        
        Returns:
            AuthenticationAPI instance for managing authentication flows
        """
        return AuthenticationAPI(manager=self)  # type: ignore[arg-type]
