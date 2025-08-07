from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.brute_force_strategy import BruteForceStrategy
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.realm_representation_localization_texts import RealmRepresentationLocalizationTexts
  from ..models.roles_representation import RolesRepresentation
  from ..models.group_representation import GroupRepresentation
  from ..models.identity_provider_representation import IdentityProviderRepresentation
  from ..models.realm_representation_attributes import RealmRepresentationAttributes
  from ..models.client_scope_representation import ClientScopeRepresentation
  from ..models.o_auth_client_representation import OAuthClientRepresentation
  from ..models.multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
  from ..models.realm_representation_smtp_server import RealmRepresentationSmtpServer
  from ..models.user_federation_provider_representation import UserFederationProviderRepresentation
  from ..models.required_action_provider_representation import RequiredActionProviderRepresentation
  from ..models.role_representation import RoleRepresentation
  from ..models.user_federation_mapper_representation import UserFederationMapperRepresentation
  from ..models.realm_representation_client_scope_mappings import RealmRepresentationClientScopeMappings
  from ..models.realm_representation_browser_security_headers import RealmRepresentationBrowserSecurityHeaders
  from ..models.identity_provider_mapper_representation import IdentityProviderMapperRepresentation
  from ..models.client_representation import ClientRepresentation
  from ..models.realm_representation_application_scope_mappings import RealmRepresentationApplicationScopeMappings
  from ..models.scope_mapping_representation import ScopeMappingRepresentation
  from ..models.client_policies_representation import ClientPoliciesRepresentation
  from ..models.realm_representation_social_providers import RealmRepresentationSocialProviders
  from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
  from ..models.client_profiles_representation import ClientProfilesRepresentation
  from ..models.authenticator_config_representation import AuthenticatorConfigRepresentation
  from ..models.organization_representation import OrganizationRepresentation
  from ..models.client_template_representation import ClientTemplateRepresentation
  from ..models.application_representation import ApplicationRepresentation
  from ..models.authentication_flow_representation import AuthenticationFlowRepresentation
  from ..models.user_representation import UserRepresentation





T = TypeVar("T", bound="RealmRepresentation")



@_attrs_define
class RealmRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            realm (Union[Unset, str]):
            display_name (Union[Unset, str]):
            display_name_html (Union[Unset, str]):
            not_before (Union[Unset, int]):
            default_signature_algorithm (Union[Unset, str]):
            revoke_refresh_token (Union[Unset, bool]):
            refresh_token_max_reuse (Union[Unset, int]):
            access_token_lifespan (Union[Unset, int]):
            access_token_lifespan_for_implicit_flow (Union[Unset, int]):
            sso_session_idle_timeout (Union[Unset, int]):
            sso_session_max_lifespan (Union[Unset, int]):
            sso_session_idle_timeout_remember_me (Union[Unset, int]):
            sso_session_max_lifespan_remember_me (Union[Unset, int]):
            offline_session_idle_timeout (Union[Unset, int]):
            offline_session_max_lifespan_enabled (Union[Unset, bool]):
            offline_session_max_lifespan (Union[Unset, int]):
            client_session_idle_timeout (Union[Unset, int]):
            client_session_max_lifespan (Union[Unset, int]):
            client_offline_session_idle_timeout (Union[Unset, int]):
            client_offline_session_max_lifespan (Union[Unset, int]):
            access_code_lifespan (Union[Unset, int]):
            access_code_lifespan_user_action (Union[Unset, int]):
            access_code_lifespan_login (Union[Unset, int]):
            action_token_generated_by_admin_lifespan (Union[Unset, int]):
            action_token_generated_by_user_lifespan (Union[Unset, int]):
            oauth_2_device_code_lifespan (Union[Unset, int]):
            oauth_2_device_polling_interval (Union[Unset, int]):
            enabled (Union[Unset, bool]):
            ssl_required (Union[Unset, str]):
            password_credential_grant_allowed (Union[Unset, bool]):
            registration_allowed (Union[Unset, bool]):
            registration_email_as_username (Union[Unset, bool]):
            remember_me (Union[Unset, bool]):
            verify_email (Union[Unset, bool]):
            login_with_email_allowed (Union[Unset, bool]):
            duplicate_emails_allowed (Union[Unset, bool]):
            reset_password_allowed (Union[Unset, bool]):
            edit_username_allowed (Union[Unset, bool]):
            user_cache_enabled (Union[Unset, bool]):
            realm_cache_enabled (Union[Unset, bool]):
            brute_force_protected (Union[Unset, bool]):
            permanent_lockout (Union[Unset, bool]):
            max_temporary_lockouts (Union[Unset, int]):
            brute_force_strategy (Union[Unset, BruteForceStrategy]):
            max_failure_wait_seconds (Union[Unset, int]):
            minimum_quick_login_wait_seconds (Union[Unset, int]):
            wait_increment_seconds (Union[Unset, int]):
            quick_login_check_milli_seconds (Union[Unset, int]):
            max_delta_time_seconds (Union[Unset, int]):
            failure_factor (Union[Unset, int]):
            private_key (Union[Unset, str]):
            public_key (Union[Unset, str]):
            certificate (Union[Unset, str]):
            code_secret (Union[Unset, str]):
            roles (Union[Unset, RolesRepresentation]):
            groups (Union[Unset, list['GroupRepresentation']]):
            default_roles (Union[Unset, list[str]]):
            default_role (Union[Unset, RoleRepresentation]):
            admin_permissions_client (Union[Unset, ClientRepresentation]):
            default_groups (Union[Unset, list[str]]):
            required_credentials (Union[Unset, list[str]]):
            password_policy (Union[Unset, str]):
            otp_policy_type (Union[Unset, str]):
            otp_policy_algorithm (Union[Unset, str]):
            otp_policy_initial_counter (Union[Unset, int]):
            otp_policy_digits (Union[Unset, int]):
            otp_policy_look_ahead_window (Union[Unset, int]):
            otp_policy_period (Union[Unset, int]):
            otp_policy_code_reusable (Union[Unset, bool]):
            otp_supported_applications (Union[Unset, list[str]]):
            localization_texts (Union[Unset, RealmRepresentationLocalizationTexts]):
            web_authn_policy_rp_entity_name (Union[Unset, str]):
            web_authn_policy_signature_algorithms (Union[Unset, list[str]]):
            web_authn_policy_rp_id (Union[Unset, str]):
            web_authn_policy_attestation_conveyance_preference (Union[Unset, str]):
            web_authn_policy_authenticator_attachment (Union[Unset, str]):
            web_authn_policy_require_resident_key (Union[Unset, str]):
            web_authn_policy_user_verification_requirement (Union[Unset, str]):
            web_authn_policy_create_timeout (Union[Unset, int]):
            web_authn_policy_avoid_same_authenticator_register (Union[Unset, bool]):
            web_authn_policy_acceptable_aaguids (Union[Unset, list[str]]):
            web_authn_policy_extra_origins (Union[Unset, list[str]]):
            web_authn_policy_passwordless_rp_entity_name (Union[Unset, str]):
            web_authn_policy_passwordless_signature_algorithms (Union[Unset, list[str]]):
            web_authn_policy_passwordless_rp_id (Union[Unset, str]):
            web_authn_policy_passwordless_attestation_conveyance_preference (Union[Unset, str]):
            web_authn_policy_passwordless_authenticator_attachment (Union[Unset, str]):
            web_authn_policy_passwordless_require_resident_key (Union[Unset, str]):
            web_authn_policy_passwordless_user_verification_requirement (Union[Unset, str]):
            web_authn_policy_passwordless_create_timeout (Union[Unset, int]):
            web_authn_policy_passwordless_avoid_same_authenticator_register (Union[Unset, bool]):
            web_authn_policy_passwordless_acceptable_aaguids (Union[Unset, list[str]]):
            web_authn_policy_passwordless_extra_origins (Union[Unset, list[str]]):
            web_authn_policy_passwordless_passkeys_enabled (Union[Unset, bool]):
            client_profiles (Union[Unset, ClientProfilesRepresentation]):
            client_policies (Union[Unset, ClientPoliciesRepresentation]):
            users (Union[Unset, list['UserRepresentation']]):
            federated_users (Union[Unset, list['UserRepresentation']]):
            scope_mappings (Union[Unset, list['ScopeMappingRepresentation']]):
            client_scope_mappings (Union[Unset, RealmRepresentationClientScopeMappings]):
            clients (Union[Unset, list['ClientRepresentation']]):
            client_scopes (Union[Unset, list['ClientScopeRepresentation']]):
            default_default_client_scopes (Union[Unset, list[str]]):
            default_optional_client_scopes (Union[Unset, list[str]]):
            browser_security_headers (Union[Unset, RealmRepresentationBrowserSecurityHeaders]):
            smtp_server (Union[Unset, RealmRepresentationSmtpServer]):
            user_federation_providers (Union[Unset, list['UserFederationProviderRepresentation']]):
            user_federation_mappers (Union[Unset, list['UserFederationMapperRepresentation']]):
            login_theme (Union[Unset, str]):
            account_theme (Union[Unset, str]):
            admin_theme (Union[Unset, str]):
            email_theme (Union[Unset, str]):
            events_enabled (Union[Unset, bool]):
            events_expiration (Union[Unset, int]):
            events_listeners (Union[Unset, list[str]]):
            enabled_event_types (Union[Unset, list[str]]):
            admin_events_enabled (Union[Unset, bool]):
            admin_events_details_enabled (Union[Unset, bool]):
            identity_providers (Union[Unset, list['IdentityProviderRepresentation']]):
            identity_provider_mappers (Union[Unset, list['IdentityProviderMapperRepresentation']]):
            protocol_mappers (Union[Unset, list['ProtocolMapperRepresentation']]):
            components (Union[Unset, MultivaluedHashMapStringComponentExportRepresentation]):
            internationalization_enabled (Union[Unset, bool]):
            supported_locales (Union[Unset, list[str]]):
            default_locale (Union[Unset, str]):
            authentication_flows (Union[Unset, list['AuthenticationFlowRepresentation']]):
            authenticator_config (Union[Unset, list['AuthenticatorConfigRepresentation']]):
            required_actions (Union[Unset, list['RequiredActionProviderRepresentation']]):
            browser_flow (Union[Unset, str]):
            registration_flow (Union[Unset, str]):
            direct_grant_flow (Union[Unset, str]):
            reset_credentials_flow (Union[Unset, str]):
            client_authentication_flow (Union[Unset, str]):
            docker_authentication_flow (Union[Unset, str]):
            first_broker_login_flow (Union[Unset, str]):
            attributes (Union[Unset, RealmRepresentationAttributes]):
            keycloak_version (Union[Unset, str]):
            user_managed_access_allowed (Union[Unset, bool]):
            organizations_enabled (Union[Unset, bool]):
            organizations (Union[Unset, list['OrganizationRepresentation']]):
            verifiable_credentials_enabled (Union[Unset, bool]):
            admin_permissions_enabled (Union[Unset, bool]):
            social (Union[Unset, bool]):
            update_profile_on_initial_social_login (Union[Unset, bool]):
            social_providers (Union[Unset, RealmRepresentationSocialProviders]):
            application_scope_mappings (Union[Unset, RealmRepresentationApplicationScopeMappings]):
            applications (Union[Unset, list['ApplicationRepresentation']]):
            oauth_clients (Union[Unset, list['OAuthClientRepresentation']]):
            client_templates (Union[Unset, list['ClientTemplateRepresentation']]):
            o_auth_2_device_code_lifespan (Union[Unset, int]):
            o_auth_2_device_polling_interval (Union[Unset, int]):
     """

    id: Union[Unset, str] = UNSET
    realm: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    display_name_html: Union[Unset, str] = UNSET
    not_before: Union[Unset, int] = UNSET
    default_signature_algorithm: Union[Unset, str] = UNSET
    revoke_refresh_token: Union[Unset, bool] = UNSET
    refresh_token_max_reuse: Union[Unset, int] = UNSET
    access_token_lifespan: Union[Unset, int] = UNSET
    access_token_lifespan_for_implicit_flow: Union[Unset, int] = UNSET
    sso_session_idle_timeout: Union[Unset, int] = UNSET
    sso_session_max_lifespan: Union[Unset, int] = UNSET
    sso_session_idle_timeout_remember_me: Union[Unset, int] = UNSET
    sso_session_max_lifespan_remember_me: Union[Unset, int] = UNSET
    offline_session_idle_timeout: Union[Unset, int] = UNSET
    offline_session_max_lifespan_enabled: Union[Unset, bool] = UNSET
    offline_session_max_lifespan: Union[Unset, int] = UNSET
    client_session_idle_timeout: Union[Unset, int] = UNSET
    client_session_max_lifespan: Union[Unset, int] = UNSET
    client_offline_session_idle_timeout: Union[Unset, int] = UNSET
    client_offline_session_max_lifespan: Union[Unset, int] = UNSET
    access_code_lifespan: Union[Unset, int] = UNSET
    access_code_lifespan_user_action: Union[Unset, int] = UNSET
    access_code_lifespan_login: Union[Unset, int] = UNSET
    action_token_generated_by_admin_lifespan: Union[Unset, int] = UNSET
    action_token_generated_by_user_lifespan: Union[Unset, int] = UNSET
    oauth_2_device_code_lifespan: Union[Unset, int] = UNSET
    oauth_2_device_polling_interval: Union[Unset, int] = UNSET
    enabled: Union[Unset, bool] = UNSET
    ssl_required: Union[Unset, str] = UNSET
    password_credential_grant_allowed: Union[Unset, bool] = UNSET
    registration_allowed: Union[Unset, bool] = UNSET
    registration_email_as_username: Union[Unset, bool] = UNSET
    remember_me: Union[Unset, bool] = UNSET
    verify_email: Union[Unset, bool] = UNSET
    login_with_email_allowed: Union[Unset, bool] = UNSET
    duplicate_emails_allowed: Union[Unset, bool] = UNSET
    reset_password_allowed: Union[Unset, bool] = UNSET
    edit_username_allowed: Union[Unset, bool] = UNSET
    user_cache_enabled: Union[Unset, bool] = UNSET
    realm_cache_enabled: Union[Unset, bool] = UNSET
    brute_force_protected: Union[Unset, bool] = UNSET
    permanent_lockout: Union[Unset, bool] = UNSET
    max_temporary_lockouts: Union[Unset, int] = UNSET
    brute_force_strategy: Union[Unset, BruteForceStrategy] = UNSET
    max_failure_wait_seconds: Union[Unset, int] = UNSET
    minimum_quick_login_wait_seconds: Union[Unset, int] = UNSET
    wait_increment_seconds: Union[Unset, int] = UNSET
    quick_login_check_milli_seconds: Union[Unset, int] = UNSET
    max_delta_time_seconds: Union[Unset, int] = UNSET
    failure_factor: Union[Unset, int] = UNSET
    private_key: Union[Unset, str] = UNSET
    public_key: Union[Unset, str] = UNSET
    certificate: Union[Unset, str] = UNSET
    code_secret: Union[Unset, str] = UNSET
    roles: Union[Unset, 'RolesRepresentation'] = UNSET
    groups: Union[Unset, list['GroupRepresentation']] = UNSET
    default_roles: Union[Unset, list[str]] = UNSET
    default_role: Union[Unset, 'RoleRepresentation'] = UNSET
    admin_permissions_client: Union[Unset, 'ClientRepresentation'] = UNSET
    default_groups: Union[Unset, list[str]] = UNSET
    required_credentials: Union[Unset, list[str]] = UNSET
    password_policy: Union[Unset, str] = UNSET
    otp_policy_type: Union[Unset, str] = UNSET
    otp_policy_algorithm: Union[Unset, str] = UNSET
    otp_policy_initial_counter: Union[Unset, int] = UNSET
    otp_policy_digits: Union[Unset, int] = UNSET
    otp_policy_look_ahead_window: Union[Unset, int] = UNSET
    otp_policy_period: Union[Unset, int] = UNSET
    otp_policy_code_reusable: Union[Unset, bool] = UNSET
    otp_supported_applications: Union[Unset, list[str]] = UNSET
    localization_texts: Union[Unset, 'RealmRepresentationLocalizationTexts'] = UNSET
    web_authn_policy_rp_entity_name: Union[Unset, str] = UNSET
    web_authn_policy_signature_algorithms: Union[Unset, list[str]] = UNSET
    web_authn_policy_rp_id: Union[Unset, str] = UNSET
    web_authn_policy_attestation_conveyance_preference: Union[Unset, str] = UNSET
    web_authn_policy_authenticator_attachment: Union[Unset, str] = UNSET
    web_authn_policy_require_resident_key: Union[Unset, str] = UNSET
    web_authn_policy_user_verification_requirement: Union[Unset, str] = UNSET
    web_authn_policy_create_timeout: Union[Unset, int] = UNSET
    web_authn_policy_avoid_same_authenticator_register: Union[Unset, bool] = UNSET
    web_authn_policy_acceptable_aaguids: Union[Unset, list[str]] = UNSET
    web_authn_policy_extra_origins: Union[Unset, list[str]] = UNSET
    web_authn_policy_passwordless_rp_entity_name: Union[Unset, str] = UNSET
    web_authn_policy_passwordless_signature_algorithms: Union[Unset, list[str]] = UNSET
    web_authn_policy_passwordless_rp_id: Union[Unset, str] = UNSET
    web_authn_policy_passwordless_attestation_conveyance_preference: Union[Unset, str] = UNSET
    web_authn_policy_passwordless_authenticator_attachment: Union[Unset, str] = UNSET
    web_authn_policy_passwordless_require_resident_key: Union[Unset, str] = UNSET
    web_authn_policy_passwordless_user_verification_requirement: Union[Unset, str] = UNSET
    web_authn_policy_passwordless_create_timeout: Union[Unset, int] = UNSET
    web_authn_policy_passwordless_avoid_same_authenticator_register: Union[Unset, bool] = UNSET
    web_authn_policy_passwordless_acceptable_aaguids: Union[Unset, list[str]] = UNSET
    web_authn_policy_passwordless_extra_origins: Union[Unset, list[str]] = UNSET
    web_authn_policy_passwordless_passkeys_enabled: Union[Unset, bool] = UNSET
    client_profiles: Union[Unset, 'ClientProfilesRepresentation'] = UNSET
    client_policies: Union[Unset, 'ClientPoliciesRepresentation'] = UNSET
    users: Union[Unset, list['UserRepresentation']] = UNSET
    federated_users: Union[Unset, list['UserRepresentation']] = UNSET
    scope_mappings: Union[Unset, list['ScopeMappingRepresentation']] = UNSET
    client_scope_mappings: Union[Unset, 'RealmRepresentationClientScopeMappings'] = UNSET
    clients: Union[Unset, list['ClientRepresentation']] = UNSET
    client_scopes: Union[Unset, list['ClientScopeRepresentation']] = UNSET
    default_default_client_scopes: Union[Unset, list[str]] = UNSET
    default_optional_client_scopes: Union[Unset, list[str]] = UNSET
    browser_security_headers: Union[Unset, 'RealmRepresentationBrowserSecurityHeaders'] = UNSET
    smtp_server: Union[Unset, 'RealmRepresentationSmtpServer'] = UNSET
    user_federation_providers: Union[Unset, list['UserFederationProviderRepresentation']] = UNSET
    user_federation_mappers: Union[Unset, list['UserFederationMapperRepresentation']] = UNSET
    login_theme: Union[Unset, str] = UNSET
    account_theme: Union[Unset, str] = UNSET
    admin_theme: Union[Unset, str] = UNSET
    email_theme: Union[Unset, str] = UNSET
    events_enabled: Union[Unset, bool] = UNSET
    events_expiration: Union[Unset, int] = UNSET
    events_listeners: Union[Unset, list[str]] = UNSET
    enabled_event_types: Union[Unset, list[str]] = UNSET
    admin_events_enabled: Union[Unset, bool] = UNSET
    admin_events_details_enabled: Union[Unset, bool] = UNSET
    identity_providers: Union[Unset, list['IdentityProviderRepresentation']] = UNSET
    identity_provider_mappers: Union[Unset, list['IdentityProviderMapperRepresentation']] = UNSET
    protocol_mappers: Union[Unset, list['ProtocolMapperRepresentation']] = UNSET
    components: Union[Unset, 'MultivaluedHashMapStringComponentExportRepresentation'] = UNSET
    internationalization_enabled: Union[Unset, bool] = UNSET
    supported_locales: Union[Unset, list[str]] = UNSET
    default_locale: Union[Unset, str] = UNSET
    authentication_flows: Union[Unset, list['AuthenticationFlowRepresentation']] = UNSET
    authenticator_config: Union[Unset, list['AuthenticatorConfigRepresentation']] = UNSET
    required_actions: Union[Unset, list['RequiredActionProviderRepresentation']] = UNSET
    browser_flow: Union[Unset, str] = UNSET
    registration_flow: Union[Unset, str] = UNSET
    direct_grant_flow: Union[Unset, str] = UNSET
    reset_credentials_flow: Union[Unset, str] = UNSET
    client_authentication_flow: Union[Unset, str] = UNSET
    docker_authentication_flow: Union[Unset, str] = UNSET
    first_broker_login_flow: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'RealmRepresentationAttributes'] = UNSET
    keycloak_version: Union[Unset, str] = UNSET
    user_managed_access_allowed: Union[Unset, bool] = UNSET
    organizations_enabled: Union[Unset, bool] = UNSET
    organizations: Union[Unset, list['OrganizationRepresentation']] = UNSET
    verifiable_credentials_enabled: Union[Unset, bool] = UNSET
    admin_permissions_enabled: Union[Unset, bool] = UNSET
    social: Union[Unset, bool] = UNSET
    update_profile_on_initial_social_login: Union[Unset, bool] = UNSET
    social_providers: Union[Unset, 'RealmRepresentationSocialProviders'] = UNSET
    application_scope_mappings: Union[Unset, 'RealmRepresentationApplicationScopeMappings'] = UNSET
    applications: Union[Unset, list['ApplicationRepresentation']] = UNSET
    oauth_clients: Union[Unset, list['OAuthClientRepresentation']] = UNSET
    client_templates: Union[Unset, list['ClientTemplateRepresentation']] = UNSET
    o_auth_2_device_code_lifespan: Union[Unset, int] = UNSET
    o_auth_2_device_polling_interval: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.realm_representation_localization_texts import RealmRepresentationLocalizationTexts
        from ..models.roles_representation import RolesRepresentation
        from ..models.group_representation import GroupRepresentation
        from ..models.identity_provider_representation import IdentityProviderRepresentation
        from ..models.realm_representation_attributes import RealmRepresentationAttributes
        from ..models.client_scope_representation import ClientScopeRepresentation
        from ..models.o_auth_client_representation import OAuthClientRepresentation
        from ..models.multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
        from ..models.realm_representation_smtp_server import RealmRepresentationSmtpServer
        from ..models.user_federation_provider_representation import UserFederationProviderRepresentation
        from ..models.required_action_provider_representation import RequiredActionProviderRepresentation
        from ..models.role_representation import RoleRepresentation
        from ..models.user_federation_mapper_representation import UserFederationMapperRepresentation
        from ..models.realm_representation_client_scope_mappings import RealmRepresentationClientScopeMappings
        from ..models.realm_representation_browser_security_headers import RealmRepresentationBrowserSecurityHeaders
        from ..models.identity_provider_mapper_representation import IdentityProviderMapperRepresentation
        from ..models.client_representation import ClientRepresentation
        from ..models.realm_representation_application_scope_mappings import RealmRepresentationApplicationScopeMappings
        from ..models.scope_mapping_representation import ScopeMappingRepresentation
        from ..models.client_policies_representation import ClientPoliciesRepresentation
        from ..models.realm_representation_social_providers import RealmRepresentationSocialProviders
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        from ..models.client_profiles_representation import ClientProfilesRepresentation
        from ..models.authenticator_config_representation import AuthenticatorConfigRepresentation
        from ..models.organization_representation import OrganizationRepresentation
        from ..models.client_template_representation import ClientTemplateRepresentation
        from ..models.application_representation import ApplicationRepresentation
        from ..models.authentication_flow_representation import AuthenticationFlowRepresentation
        from ..models.user_representation import UserRepresentation
        id = self.id

        realm = self.realm

        display_name = self.display_name

        display_name_html = self.display_name_html

        not_before = self.not_before

        default_signature_algorithm = self.default_signature_algorithm

        revoke_refresh_token = self.revoke_refresh_token

        refresh_token_max_reuse = self.refresh_token_max_reuse

        access_token_lifespan = self.access_token_lifespan

        access_token_lifespan_for_implicit_flow = self.access_token_lifespan_for_implicit_flow

        sso_session_idle_timeout = self.sso_session_idle_timeout

        sso_session_max_lifespan = self.sso_session_max_lifespan

        sso_session_idle_timeout_remember_me = self.sso_session_idle_timeout_remember_me

        sso_session_max_lifespan_remember_me = self.sso_session_max_lifespan_remember_me

        offline_session_idle_timeout = self.offline_session_idle_timeout

        offline_session_max_lifespan_enabled = self.offline_session_max_lifespan_enabled

        offline_session_max_lifespan = self.offline_session_max_lifespan

        client_session_idle_timeout = self.client_session_idle_timeout

        client_session_max_lifespan = self.client_session_max_lifespan

        client_offline_session_idle_timeout = self.client_offline_session_idle_timeout

        client_offline_session_max_lifespan = self.client_offline_session_max_lifespan

        access_code_lifespan = self.access_code_lifespan

        access_code_lifespan_user_action = self.access_code_lifespan_user_action

        access_code_lifespan_login = self.access_code_lifespan_login

        action_token_generated_by_admin_lifespan = self.action_token_generated_by_admin_lifespan

        action_token_generated_by_user_lifespan = self.action_token_generated_by_user_lifespan

        oauth_2_device_code_lifespan = self.oauth_2_device_code_lifespan

        oauth_2_device_polling_interval = self.oauth_2_device_polling_interval

        enabled = self.enabled

        ssl_required = self.ssl_required

        password_credential_grant_allowed = self.password_credential_grant_allowed

        registration_allowed = self.registration_allowed

        registration_email_as_username = self.registration_email_as_username

        remember_me = self.remember_me

        verify_email = self.verify_email

        login_with_email_allowed = self.login_with_email_allowed

        duplicate_emails_allowed = self.duplicate_emails_allowed

        reset_password_allowed = self.reset_password_allowed

        edit_username_allowed = self.edit_username_allowed

        user_cache_enabled = self.user_cache_enabled

        realm_cache_enabled = self.realm_cache_enabled

        brute_force_protected = self.brute_force_protected

        permanent_lockout = self.permanent_lockout

        max_temporary_lockouts = self.max_temporary_lockouts

        brute_force_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.brute_force_strategy, Unset):
            brute_force_strategy = self.brute_force_strategy.value


        max_failure_wait_seconds = self.max_failure_wait_seconds

        minimum_quick_login_wait_seconds = self.minimum_quick_login_wait_seconds

        wait_increment_seconds = self.wait_increment_seconds

        quick_login_check_milli_seconds = self.quick_login_check_milli_seconds

        max_delta_time_seconds = self.max_delta_time_seconds

        failure_factor = self.failure_factor

        private_key = self.private_key

        public_key = self.public_key

        certificate = self.certificate

        code_secret = self.code_secret

        roles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles.to_dict()

        groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)



        default_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.default_roles, Unset):
            default_roles = self.default_roles



        default_role: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.default_role, Unset):
            default_role = self.default_role.to_dict()

        admin_permissions_client: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.admin_permissions_client, Unset):
            admin_permissions_client = self.admin_permissions_client.to_dict()

        default_groups: Union[Unset, list[str]] = UNSET
        if not isinstance(self.default_groups, Unset):
            default_groups = self.default_groups



        required_credentials: Union[Unset, list[str]] = UNSET
        if not isinstance(self.required_credentials, Unset):
            required_credentials = self.required_credentials



        password_policy = self.password_policy

        otp_policy_type = self.otp_policy_type

        otp_policy_algorithm = self.otp_policy_algorithm

        otp_policy_initial_counter = self.otp_policy_initial_counter

        otp_policy_digits = self.otp_policy_digits

        otp_policy_look_ahead_window = self.otp_policy_look_ahead_window

        otp_policy_period = self.otp_policy_period

        otp_policy_code_reusable = self.otp_policy_code_reusable

        otp_supported_applications: Union[Unset, list[str]] = UNSET
        if not isinstance(self.otp_supported_applications, Unset):
            otp_supported_applications = self.otp_supported_applications



        localization_texts: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.localization_texts, Unset):
            localization_texts = self.localization_texts.to_dict()

        web_authn_policy_rp_entity_name = self.web_authn_policy_rp_entity_name

        web_authn_policy_signature_algorithms: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_authn_policy_signature_algorithms, Unset):
            web_authn_policy_signature_algorithms = self.web_authn_policy_signature_algorithms



        web_authn_policy_rp_id = self.web_authn_policy_rp_id

        web_authn_policy_attestation_conveyance_preference = self.web_authn_policy_attestation_conveyance_preference

        web_authn_policy_authenticator_attachment = self.web_authn_policy_authenticator_attachment

        web_authn_policy_require_resident_key = self.web_authn_policy_require_resident_key

        web_authn_policy_user_verification_requirement = self.web_authn_policy_user_verification_requirement

        web_authn_policy_create_timeout = self.web_authn_policy_create_timeout

        web_authn_policy_avoid_same_authenticator_register = self.web_authn_policy_avoid_same_authenticator_register

        web_authn_policy_acceptable_aaguids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_authn_policy_acceptable_aaguids, Unset):
            web_authn_policy_acceptable_aaguids = self.web_authn_policy_acceptable_aaguids



        web_authn_policy_extra_origins: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_authn_policy_extra_origins, Unset):
            web_authn_policy_extra_origins = self.web_authn_policy_extra_origins



        web_authn_policy_passwordless_rp_entity_name = self.web_authn_policy_passwordless_rp_entity_name

        web_authn_policy_passwordless_signature_algorithms: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_authn_policy_passwordless_signature_algorithms, Unset):
            web_authn_policy_passwordless_signature_algorithms = self.web_authn_policy_passwordless_signature_algorithms



        web_authn_policy_passwordless_rp_id = self.web_authn_policy_passwordless_rp_id

        web_authn_policy_passwordless_attestation_conveyance_preference = self.web_authn_policy_passwordless_attestation_conveyance_preference

        web_authn_policy_passwordless_authenticator_attachment = self.web_authn_policy_passwordless_authenticator_attachment

        web_authn_policy_passwordless_require_resident_key = self.web_authn_policy_passwordless_require_resident_key

        web_authn_policy_passwordless_user_verification_requirement = self.web_authn_policy_passwordless_user_verification_requirement

        web_authn_policy_passwordless_create_timeout = self.web_authn_policy_passwordless_create_timeout

        web_authn_policy_passwordless_avoid_same_authenticator_register = self.web_authn_policy_passwordless_avoid_same_authenticator_register

        web_authn_policy_passwordless_acceptable_aaguids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_authn_policy_passwordless_acceptable_aaguids, Unset):
            web_authn_policy_passwordless_acceptable_aaguids = self.web_authn_policy_passwordless_acceptable_aaguids



        web_authn_policy_passwordless_extra_origins: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_authn_policy_passwordless_extra_origins, Unset):
            web_authn_policy_passwordless_extra_origins = self.web_authn_policy_passwordless_extra_origins



        web_authn_policy_passwordless_passkeys_enabled = self.web_authn_policy_passwordless_passkeys_enabled

        client_profiles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client_profiles, Unset):
            client_profiles = self.client_profiles.to_dict()

        client_policies: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client_policies, Unset):
            client_policies = self.client_policies.to_dict()

        users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.users, Unset):
            users = []
            for users_item_data in self.users:
                users_item = users_item_data.to_dict()
                users.append(users_item)



        federated_users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.federated_users, Unset):
            federated_users = []
            for federated_users_item_data in self.federated_users:
                federated_users_item = federated_users_item_data.to_dict()
                federated_users.append(federated_users_item)



        scope_mappings: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.scope_mappings, Unset):
            scope_mappings = []
            for scope_mappings_item_data in self.scope_mappings:
                scope_mappings_item = scope_mappings_item_data.to_dict()
                scope_mappings.append(scope_mappings_item)



        client_scope_mappings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client_scope_mappings, Unset):
            client_scope_mappings = self.client_scope_mappings.to_dict()

        clients: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.clients, Unset):
            clients = []
            for clients_item_data in self.clients:
                clients_item = clients_item_data.to_dict()
                clients.append(clients_item)



        client_scopes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.client_scopes, Unset):
            client_scopes = []
            for client_scopes_item_data in self.client_scopes:
                client_scopes_item = client_scopes_item_data.to_dict()
                client_scopes.append(client_scopes_item)



        default_default_client_scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.default_default_client_scopes, Unset):
            default_default_client_scopes = self.default_default_client_scopes



        default_optional_client_scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.default_optional_client_scopes, Unset):
            default_optional_client_scopes = self.default_optional_client_scopes



        browser_security_headers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.browser_security_headers, Unset):
            browser_security_headers = self.browser_security_headers.to_dict()

        smtp_server: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.smtp_server, Unset):
            smtp_server = self.smtp_server.to_dict()

        user_federation_providers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.user_federation_providers, Unset):
            user_federation_providers = []
            for user_federation_providers_item_data in self.user_federation_providers:
                user_federation_providers_item = user_federation_providers_item_data.to_dict()
                user_federation_providers.append(user_federation_providers_item)



        user_federation_mappers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.user_federation_mappers, Unset):
            user_federation_mappers = []
            for user_federation_mappers_item_data in self.user_federation_mappers:
                user_federation_mappers_item = user_federation_mappers_item_data.to_dict()
                user_federation_mappers.append(user_federation_mappers_item)



        login_theme = self.login_theme

        account_theme = self.account_theme

        admin_theme = self.admin_theme

        email_theme = self.email_theme

        events_enabled = self.events_enabled

        events_expiration = self.events_expiration

        events_listeners: Union[Unset, list[str]] = UNSET
        if not isinstance(self.events_listeners, Unset):
            events_listeners = self.events_listeners



        enabled_event_types: Union[Unset, list[str]] = UNSET
        if not isinstance(self.enabled_event_types, Unset):
            enabled_event_types = self.enabled_event_types



        admin_events_enabled = self.admin_events_enabled

        admin_events_details_enabled = self.admin_events_details_enabled

        identity_providers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.identity_providers, Unset):
            identity_providers = []
            for identity_providers_item_data in self.identity_providers:
                identity_providers_item = identity_providers_item_data.to_dict()
                identity_providers.append(identity_providers_item)



        identity_provider_mappers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.identity_provider_mappers, Unset):
            identity_provider_mappers = []
            for identity_provider_mappers_item_data in self.identity_provider_mappers:
                identity_provider_mappers_item = identity_provider_mappers_item_data.to_dict()
                identity_provider_mappers.append(identity_provider_mappers_item)



        protocol_mappers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.protocol_mappers, Unset):
            protocol_mappers = []
            for protocol_mappers_item_data in self.protocol_mappers:
                protocol_mappers_item = protocol_mappers_item_data.to_dict()
                protocol_mappers.append(protocol_mappers_item)



        components: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.components, Unset):
            components = self.components.to_dict()

        internationalization_enabled = self.internationalization_enabled

        supported_locales: Union[Unset, list[str]] = UNSET
        if not isinstance(self.supported_locales, Unset):
            supported_locales = self.supported_locales



        default_locale = self.default_locale

        authentication_flows: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authentication_flows, Unset):
            authentication_flows = []
            for authentication_flows_item_data in self.authentication_flows:
                authentication_flows_item = authentication_flows_item_data.to_dict()
                authentication_flows.append(authentication_flows_item)



        authenticator_config: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authenticator_config, Unset):
            authenticator_config = []
            for authenticator_config_item_data in self.authenticator_config:
                authenticator_config_item = authenticator_config_item_data.to_dict()
                authenticator_config.append(authenticator_config_item)



        required_actions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.required_actions, Unset):
            required_actions = []
            for required_actions_item_data in self.required_actions:
                required_actions_item = required_actions_item_data.to_dict()
                required_actions.append(required_actions_item)



        browser_flow = self.browser_flow

        registration_flow = self.registration_flow

        direct_grant_flow = self.direct_grant_flow

        reset_credentials_flow = self.reset_credentials_flow

        client_authentication_flow = self.client_authentication_flow

        docker_authentication_flow = self.docker_authentication_flow

        first_broker_login_flow = self.first_broker_login_flow

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        keycloak_version = self.keycloak_version

        user_managed_access_allowed = self.user_managed_access_allowed

        organizations_enabled = self.organizations_enabled

        organizations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.organizations, Unset):
            organizations = []
            for organizations_item_data in self.organizations:
                organizations_item = organizations_item_data.to_dict()
                organizations.append(organizations_item)



        verifiable_credentials_enabled = self.verifiable_credentials_enabled

        admin_permissions_enabled = self.admin_permissions_enabled

        social = self.social

        update_profile_on_initial_social_login = self.update_profile_on_initial_social_login

        social_providers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.social_providers, Unset):
            social_providers = self.social_providers.to_dict()

        application_scope_mappings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.application_scope_mappings, Unset):
            application_scope_mappings = self.application_scope_mappings.to_dict()

        applications: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.applications, Unset):
            applications = []
            for applications_item_data in self.applications:
                applications_item = applications_item_data.to_dict()
                applications.append(applications_item)



        oauth_clients: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.oauth_clients, Unset):
            oauth_clients = []
            for oauth_clients_item_data in self.oauth_clients:
                oauth_clients_item = oauth_clients_item_data.to_dict()
                oauth_clients.append(oauth_clients_item)



        client_templates: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.client_templates, Unset):
            client_templates = []
            for client_templates_item_data in self.client_templates:
                client_templates_item = client_templates_item_data.to_dict()
                client_templates.append(client_templates_item)



        o_auth_2_device_code_lifespan = self.o_auth_2_device_code_lifespan

        o_auth_2_device_polling_interval = self.o_auth_2_device_polling_interval


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if realm is not UNSET:
            field_dict["realm"] = realm
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if display_name_html is not UNSET:
            field_dict["displayNameHtml"] = display_name_html
        if not_before is not UNSET:
            field_dict["notBefore"] = not_before
        if default_signature_algorithm is not UNSET:
            field_dict["defaultSignatureAlgorithm"] = default_signature_algorithm
        if revoke_refresh_token is not UNSET:
            field_dict["revokeRefreshToken"] = revoke_refresh_token
        if refresh_token_max_reuse is not UNSET:
            field_dict["refreshTokenMaxReuse"] = refresh_token_max_reuse
        if access_token_lifespan is not UNSET:
            field_dict["accessTokenLifespan"] = access_token_lifespan
        if access_token_lifespan_for_implicit_flow is not UNSET:
            field_dict["accessTokenLifespanForImplicitFlow"] = access_token_lifespan_for_implicit_flow
        if sso_session_idle_timeout is not UNSET:
            field_dict["ssoSessionIdleTimeout"] = sso_session_idle_timeout
        if sso_session_max_lifespan is not UNSET:
            field_dict["ssoSessionMaxLifespan"] = sso_session_max_lifespan
        if sso_session_idle_timeout_remember_me is not UNSET:
            field_dict["ssoSessionIdleTimeoutRememberMe"] = sso_session_idle_timeout_remember_me
        if sso_session_max_lifespan_remember_me is not UNSET:
            field_dict["ssoSessionMaxLifespanRememberMe"] = sso_session_max_lifespan_remember_me
        if offline_session_idle_timeout is not UNSET:
            field_dict["offlineSessionIdleTimeout"] = offline_session_idle_timeout
        if offline_session_max_lifespan_enabled is not UNSET:
            field_dict["offlineSessionMaxLifespanEnabled"] = offline_session_max_lifespan_enabled
        if offline_session_max_lifespan is not UNSET:
            field_dict["offlineSessionMaxLifespan"] = offline_session_max_lifespan
        if client_session_idle_timeout is not UNSET:
            field_dict["clientSessionIdleTimeout"] = client_session_idle_timeout
        if client_session_max_lifespan is not UNSET:
            field_dict["clientSessionMaxLifespan"] = client_session_max_lifespan
        if client_offline_session_idle_timeout is not UNSET:
            field_dict["clientOfflineSessionIdleTimeout"] = client_offline_session_idle_timeout
        if client_offline_session_max_lifespan is not UNSET:
            field_dict["clientOfflineSessionMaxLifespan"] = client_offline_session_max_lifespan
        if access_code_lifespan is not UNSET:
            field_dict["accessCodeLifespan"] = access_code_lifespan
        if access_code_lifespan_user_action is not UNSET:
            field_dict["accessCodeLifespanUserAction"] = access_code_lifespan_user_action
        if access_code_lifespan_login is not UNSET:
            field_dict["accessCodeLifespanLogin"] = access_code_lifespan_login
        if action_token_generated_by_admin_lifespan is not UNSET:
            field_dict["actionTokenGeneratedByAdminLifespan"] = action_token_generated_by_admin_lifespan
        if action_token_generated_by_user_lifespan is not UNSET:
            field_dict["actionTokenGeneratedByUserLifespan"] = action_token_generated_by_user_lifespan
        if oauth_2_device_code_lifespan is not UNSET:
            field_dict["oauth2DeviceCodeLifespan"] = oauth_2_device_code_lifespan
        if oauth_2_device_polling_interval is not UNSET:
            field_dict["oauth2DevicePollingInterval"] = oauth_2_device_polling_interval
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if ssl_required is not UNSET:
            field_dict["sslRequired"] = ssl_required
        if password_credential_grant_allowed is not UNSET:
            field_dict["passwordCredentialGrantAllowed"] = password_credential_grant_allowed
        if registration_allowed is not UNSET:
            field_dict["registrationAllowed"] = registration_allowed
        if registration_email_as_username is not UNSET:
            field_dict["registrationEmailAsUsername"] = registration_email_as_username
        if remember_me is not UNSET:
            field_dict["rememberMe"] = remember_me
        if verify_email is not UNSET:
            field_dict["verifyEmail"] = verify_email
        if login_with_email_allowed is not UNSET:
            field_dict["loginWithEmailAllowed"] = login_with_email_allowed
        if duplicate_emails_allowed is not UNSET:
            field_dict["duplicateEmailsAllowed"] = duplicate_emails_allowed
        if reset_password_allowed is not UNSET:
            field_dict["resetPasswordAllowed"] = reset_password_allowed
        if edit_username_allowed is not UNSET:
            field_dict["editUsernameAllowed"] = edit_username_allowed
        if user_cache_enabled is not UNSET:
            field_dict["userCacheEnabled"] = user_cache_enabled
        if realm_cache_enabled is not UNSET:
            field_dict["realmCacheEnabled"] = realm_cache_enabled
        if brute_force_protected is not UNSET:
            field_dict["bruteForceProtected"] = brute_force_protected
        if permanent_lockout is not UNSET:
            field_dict["permanentLockout"] = permanent_lockout
        if max_temporary_lockouts is not UNSET:
            field_dict["maxTemporaryLockouts"] = max_temporary_lockouts
        if brute_force_strategy is not UNSET:
            field_dict["bruteForceStrategy"] = brute_force_strategy
        if max_failure_wait_seconds is not UNSET:
            field_dict["maxFailureWaitSeconds"] = max_failure_wait_seconds
        if minimum_quick_login_wait_seconds is not UNSET:
            field_dict["minimumQuickLoginWaitSeconds"] = minimum_quick_login_wait_seconds
        if wait_increment_seconds is not UNSET:
            field_dict["waitIncrementSeconds"] = wait_increment_seconds
        if quick_login_check_milli_seconds is not UNSET:
            field_dict["quickLoginCheckMilliSeconds"] = quick_login_check_milli_seconds
        if max_delta_time_seconds is not UNSET:
            field_dict["maxDeltaTimeSeconds"] = max_delta_time_seconds
        if failure_factor is not UNSET:
            field_dict["failureFactor"] = failure_factor
        if private_key is not UNSET:
            field_dict["privateKey"] = private_key
        if public_key is not UNSET:
            field_dict["publicKey"] = public_key
        if certificate is not UNSET:
            field_dict["certificate"] = certificate
        if code_secret is not UNSET:
            field_dict["codeSecret"] = code_secret
        if roles is not UNSET:
            field_dict["roles"] = roles
        if groups is not UNSET:
            field_dict["groups"] = groups
        if default_roles is not UNSET:
            field_dict["defaultRoles"] = default_roles
        if default_role is not UNSET:
            field_dict["defaultRole"] = default_role
        if admin_permissions_client is not UNSET:
            field_dict["adminPermissionsClient"] = admin_permissions_client
        if default_groups is not UNSET:
            field_dict["defaultGroups"] = default_groups
        if required_credentials is not UNSET:
            field_dict["requiredCredentials"] = required_credentials
        if password_policy is not UNSET:
            field_dict["passwordPolicy"] = password_policy
        if otp_policy_type is not UNSET:
            field_dict["otpPolicyType"] = otp_policy_type
        if otp_policy_algorithm is not UNSET:
            field_dict["otpPolicyAlgorithm"] = otp_policy_algorithm
        if otp_policy_initial_counter is not UNSET:
            field_dict["otpPolicyInitialCounter"] = otp_policy_initial_counter
        if otp_policy_digits is not UNSET:
            field_dict["otpPolicyDigits"] = otp_policy_digits
        if otp_policy_look_ahead_window is not UNSET:
            field_dict["otpPolicyLookAheadWindow"] = otp_policy_look_ahead_window
        if otp_policy_period is not UNSET:
            field_dict["otpPolicyPeriod"] = otp_policy_period
        if otp_policy_code_reusable is not UNSET:
            field_dict["otpPolicyCodeReusable"] = otp_policy_code_reusable
        if otp_supported_applications is not UNSET:
            field_dict["otpSupportedApplications"] = otp_supported_applications
        if localization_texts is not UNSET:
            field_dict["localizationTexts"] = localization_texts
        if web_authn_policy_rp_entity_name is not UNSET:
            field_dict["webAuthnPolicyRpEntityName"] = web_authn_policy_rp_entity_name
        if web_authn_policy_signature_algorithms is not UNSET:
            field_dict["webAuthnPolicySignatureAlgorithms"] = web_authn_policy_signature_algorithms
        if web_authn_policy_rp_id is not UNSET:
            field_dict["webAuthnPolicyRpId"] = web_authn_policy_rp_id
        if web_authn_policy_attestation_conveyance_preference is not UNSET:
            field_dict["webAuthnPolicyAttestationConveyancePreference"] = web_authn_policy_attestation_conveyance_preference
        if web_authn_policy_authenticator_attachment is not UNSET:
            field_dict["webAuthnPolicyAuthenticatorAttachment"] = web_authn_policy_authenticator_attachment
        if web_authn_policy_require_resident_key is not UNSET:
            field_dict["webAuthnPolicyRequireResidentKey"] = web_authn_policy_require_resident_key
        if web_authn_policy_user_verification_requirement is not UNSET:
            field_dict["webAuthnPolicyUserVerificationRequirement"] = web_authn_policy_user_verification_requirement
        if web_authn_policy_create_timeout is not UNSET:
            field_dict["webAuthnPolicyCreateTimeout"] = web_authn_policy_create_timeout
        if web_authn_policy_avoid_same_authenticator_register is not UNSET:
            field_dict["webAuthnPolicyAvoidSameAuthenticatorRegister"] = web_authn_policy_avoid_same_authenticator_register
        if web_authn_policy_acceptable_aaguids is not UNSET:
            field_dict["webAuthnPolicyAcceptableAaguids"] = web_authn_policy_acceptable_aaguids
        if web_authn_policy_extra_origins is not UNSET:
            field_dict["webAuthnPolicyExtraOrigins"] = web_authn_policy_extra_origins
        if web_authn_policy_passwordless_rp_entity_name is not UNSET:
            field_dict["webAuthnPolicyPasswordlessRpEntityName"] = web_authn_policy_passwordless_rp_entity_name
        if web_authn_policy_passwordless_signature_algorithms is not UNSET:
            field_dict["webAuthnPolicyPasswordlessSignatureAlgorithms"] = web_authn_policy_passwordless_signature_algorithms
        if web_authn_policy_passwordless_rp_id is not UNSET:
            field_dict["webAuthnPolicyPasswordlessRpId"] = web_authn_policy_passwordless_rp_id
        if web_authn_policy_passwordless_attestation_conveyance_preference is not UNSET:
            field_dict["webAuthnPolicyPasswordlessAttestationConveyancePreference"] = web_authn_policy_passwordless_attestation_conveyance_preference
        if web_authn_policy_passwordless_authenticator_attachment is not UNSET:
            field_dict["webAuthnPolicyPasswordlessAuthenticatorAttachment"] = web_authn_policy_passwordless_authenticator_attachment
        if web_authn_policy_passwordless_require_resident_key is not UNSET:
            field_dict["webAuthnPolicyPasswordlessRequireResidentKey"] = web_authn_policy_passwordless_require_resident_key
        if web_authn_policy_passwordless_user_verification_requirement is not UNSET:
            field_dict["webAuthnPolicyPasswordlessUserVerificationRequirement"] = web_authn_policy_passwordless_user_verification_requirement
        if web_authn_policy_passwordless_create_timeout is not UNSET:
            field_dict["webAuthnPolicyPasswordlessCreateTimeout"] = web_authn_policy_passwordless_create_timeout
        if web_authn_policy_passwordless_avoid_same_authenticator_register is not UNSET:
            field_dict["webAuthnPolicyPasswordlessAvoidSameAuthenticatorRegister"] = web_authn_policy_passwordless_avoid_same_authenticator_register
        if web_authn_policy_passwordless_acceptable_aaguids is not UNSET:
            field_dict["webAuthnPolicyPasswordlessAcceptableAaguids"] = web_authn_policy_passwordless_acceptable_aaguids
        if web_authn_policy_passwordless_extra_origins is not UNSET:
            field_dict["webAuthnPolicyPasswordlessExtraOrigins"] = web_authn_policy_passwordless_extra_origins
        if web_authn_policy_passwordless_passkeys_enabled is not UNSET:
            field_dict["webAuthnPolicyPasswordlessPasskeysEnabled"] = web_authn_policy_passwordless_passkeys_enabled
        if client_profiles is not UNSET:
            field_dict["clientProfiles"] = client_profiles
        if client_policies is not UNSET:
            field_dict["clientPolicies"] = client_policies
        if users is not UNSET:
            field_dict["users"] = users
        if federated_users is not UNSET:
            field_dict["federatedUsers"] = federated_users
        if scope_mappings is not UNSET:
            field_dict["scopeMappings"] = scope_mappings
        if client_scope_mappings is not UNSET:
            field_dict["clientScopeMappings"] = client_scope_mappings
        if clients is not UNSET:
            field_dict["clients"] = clients
        if client_scopes is not UNSET:
            field_dict["clientScopes"] = client_scopes
        if default_default_client_scopes is not UNSET:
            field_dict["defaultDefaultClientScopes"] = default_default_client_scopes
        if default_optional_client_scopes is not UNSET:
            field_dict["defaultOptionalClientScopes"] = default_optional_client_scopes
        if browser_security_headers is not UNSET:
            field_dict["browserSecurityHeaders"] = browser_security_headers
        if smtp_server is not UNSET:
            field_dict["smtpServer"] = smtp_server
        if user_federation_providers is not UNSET:
            field_dict["userFederationProviders"] = user_federation_providers
        if user_federation_mappers is not UNSET:
            field_dict["userFederationMappers"] = user_federation_mappers
        if login_theme is not UNSET:
            field_dict["loginTheme"] = login_theme
        if account_theme is not UNSET:
            field_dict["accountTheme"] = account_theme
        if admin_theme is not UNSET:
            field_dict["adminTheme"] = admin_theme
        if email_theme is not UNSET:
            field_dict["emailTheme"] = email_theme
        if events_enabled is not UNSET:
            field_dict["eventsEnabled"] = events_enabled
        if events_expiration is not UNSET:
            field_dict["eventsExpiration"] = events_expiration
        if events_listeners is not UNSET:
            field_dict["eventsListeners"] = events_listeners
        if enabled_event_types is not UNSET:
            field_dict["enabledEventTypes"] = enabled_event_types
        if admin_events_enabled is not UNSET:
            field_dict["adminEventsEnabled"] = admin_events_enabled
        if admin_events_details_enabled is not UNSET:
            field_dict["adminEventsDetailsEnabled"] = admin_events_details_enabled
        if identity_providers is not UNSET:
            field_dict["identityProviders"] = identity_providers
        if identity_provider_mappers is not UNSET:
            field_dict["identityProviderMappers"] = identity_provider_mappers
        if protocol_mappers is not UNSET:
            field_dict["protocolMappers"] = protocol_mappers
        if components is not UNSET:
            field_dict["components"] = components
        if internationalization_enabled is not UNSET:
            field_dict["internationalizationEnabled"] = internationalization_enabled
        if supported_locales is not UNSET:
            field_dict["supportedLocales"] = supported_locales
        if default_locale is not UNSET:
            field_dict["defaultLocale"] = default_locale
        if authentication_flows is not UNSET:
            field_dict["authenticationFlows"] = authentication_flows
        if authenticator_config is not UNSET:
            field_dict["authenticatorConfig"] = authenticator_config
        if required_actions is not UNSET:
            field_dict["requiredActions"] = required_actions
        if browser_flow is not UNSET:
            field_dict["browserFlow"] = browser_flow
        if registration_flow is not UNSET:
            field_dict["registrationFlow"] = registration_flow
        if direct_grant_flow is not UNSET:
            field_dict["directGrantFlow"] = direct_grant_flow
        if reset_credentials_flow is not UNSET:
            field_dict["resetCredentialsFlow"] = reset_credentials_flow
        if client_authentication_flow is not UNSET:
            field_dict["clientAuthenticationFlow"] = client_authentication_flow
        if docker_authentication_flow is not UNSET:
            field_dict["dockerAuthenticationFlow"] = docker_authentication_flow
        if first_broker_login_flow is not UNSET:
            field_dict["firstBrokerLoginFlow"] = first_broker_login_flow
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if keycloak_version is not UNSET:
            field_dict["keycloakVersion"] = keycloak_version
        if user_managed_access_allowed is not UNSET:
            field_dict["userManagedAccessAllowed"] = user_managed_access_allowed
        if organizations_enabled is not UNSET:
            field_dict["organizationsEnabled"] = organizations_enabled
        if organizations is not UNSET:
            field_dict["organizations"] = organizations
        if verifiable_credentials_enabled is not UNSET:
            field_dict["verifiableCredentialsEnabled"] = verifiable_credentials_enabled
        if admin_permissions_enabled is not UNSET:
            field_dict["adminPermissionsEnabled"] = admin_permissions_enabled
        if social is not UNSET:
            field_dict["social"] = social
        if update_profile_on_initial_social_login is not UNSET:
            field_dict["updateProfileOnInitialSocialLogin"] = update_profile_on_initial_social_login
        if social_providers is not UNSET:
            field_dict["socialProviders"] = social_providers
        if application_scope_mappings is not UNSET:
            field_dict["applicationScopeMappings"] = application_scope_mappings
        if applications is not UNSET:
            field_dict["applications"] = applications
        if oauth_clients is not UNSET:
            field_dict["oauthClients"] = oauth_clients
        if client_templates is not UNSET:
            field_dict["clientTemplates"] = client_templates
        if o_auth_2_device_code_lifespan is not UNSET:
            field_dict["oAuth2DeviceCodeLifespan"] = o_auth_2_device_code_lifespan
        if o_auth_2_device_polling_interval is not UNSET:
            field_dict["oAuth2DevicePollingInterval"] = o_auth_2_device_polling_interval

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.realm_representation_localization_texts import RealmRepresentationLocalizationTexts
        from ..models.roles_representation import RolesRepresentation
        from ..models.group_representation import GroupRepresentation
        from ..models.identity_provider_representation import IdentityProviderRepresentation
        from ..models.realm_representation_attributes import RealmRepresentationAttributes
        from ..models.client_scope_representation import ClientScopeRepresentation
        from ..models.o_auth_client_representation import OAuthClientRepresentation
        from ..models.multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
        from ..models.realm_representation_smtp_server import RealmRepresentationSmtpServer
        from ..models.user_federation_provider_representation import UserFederationProviderRepresentation
        from ..models.required_action_provider_representation import RequiredActionProviderRepresentation
        from ..models.role_representation import RoleRepresentation
        from ..models.user_federation_mapper_representation import UserFederationMapperRepresentation
        from ..models.realm_representation_client_scope_mappings import RealmRepresentationClientScopeMappings
        from ..models.realm_representation_browser_security_headers import RealmRepresentationBrowserSecurityHeaders
        from ..models.identity_provider_mapper_representation import IdentityProviderMapperRepresentation
        from ..models.client_representation import ClientRepresentation
        from ..models.realm_representation_application_scope_mappings import RealmRepresentationApplicationScopeMappings
        from ..models.scope_mapping_representation import ScopeMappingRepresentation
        from ..models.client_policies_representation import ClientPoliciesRepresentation
        from ..models.realm_representation_social_providers import RealmRepresentationSocialProviders
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        from ..models.client_profiles_representation import ClientProfilesRepresentation
        from ..models.authenticator_config_representation import AuthenticatorConfigRepresentation
        from ..models.organization_representation import OrganizationRepresentation
        from ..models.client_template_representation import ClientTemplateRepresentation
        from ..models.application_representation import ApplicationRepresentation
        from ..models.authentication_flow_representation import AuthenticationFlowRepresentation
        from ..models.user_representation import UserRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        realm = d.pop("realm", UNSET)

        display_name = d.pop("displayName", UNSET)

        display_name_html = d.pop("displayNameHtml", UNSET)

        not_before = d.pop("notBefore", UNSET)

        default_signature_algorithm = d.pop("defaultSignatureAlgorithm", UNSET)

        revoke_refresh_token = d.pop("revokeRefreshToken", UNSET)

        refresh_token_max_reuse = d.pop("refreshTokenMaxReuse", UNSET)

        access_token_lifespan = d.pop("accessTokenLifespan", UNSET)

        access_token_lifespan_for_implicit_flow = d.pop("accessTokenLifespanForImplicitFlow", UNSET)

        sso_session_idle_timeout = d.pop("ssoSessionIdleTimeout", UNSET)

        sso_session_max_lifespan = d.pop("ssoSessionMaxLifespan", UNSET)

        sso_session_idle_timeout_remember_me = d.pop("ssoSessionIdleTimeoutRememberMe", UNSET)

        sso_session_max_lifespan_remember_me = d.pop("ssoSessionMaxLifespanRememberMe", UNSET)

        offline_session_idle_timeout = d.pop("offlineSessionIdleTimeout", UNSET)

        offline_session_max_lifespan_enabled = d.pop("offlineSessionMaxLifespanEnabled", UNSET)

        offline_session_max_lifespan = d.pop("offlineSessionMaxLifespan", UNSET)

        client_session_idle_timeout = d.pop("clientSessionIdleTimeout", UNSET)

        client_session_max_lifespan = d.pop("clientSessionMaxLifespan", UNSET)

        client_offline_session_idle_timeout = d.pop("clientOfflineSessionIdleTimeout", UNSET)

        client_offline_session_max_lifespan = d.pop("clientOfflineSessionMaxLifespan", UNSET)

        access_code_lifespan = d.pop("accessCodeLifespan", UNSET)

        access_code_lifespan_user_action = d.pop("accessCodeLifespanUserAction", UNSET)

        access_code_lifespan_login = d.pop("accessCodeLifespanLogin", UNSET)

        action_token_generated_by_admin_lifespan = d.pop("actionTokenGeneratedByAdminLifespan", UNSET)

        action_token_generated_by_user_lifespan = d.pop("actionTokenGeneratedByUserLifespan", UNSET)

        oauth_2_device_code_lifespan = d.pop("oauth2DeviceCodeLifespan", UNSET)

        oauth_2_device_polling_interval = d.pop("oauth2DevicePollingInterval", UNSET)

        enabled = d.pop("enabled", UNSET)

        ssl_required = d.pop("sslRequired", UNSET)

        password_credential_grant_allowed = d.pop("passwordCredentialGrantAllowed", UNSET)

        registration_allowed = d.pop("registrationAllowed", UNSET)

        registration_email_as_username = d.pop("registrationEmailAsUsername", UNSET)

        remember_me = d.pop("rememberMe", UNSET)

        verify_email = d.pop("verifyEmail", UNSET)

        login_with_email_allowed = d.pop("loginWithEmailAllowed", UNSET)

        duplicate_emails_allowed = d.pop("duplicateEmailsAllowed", UNSET)

        reset_password_allowed = d.pop("resetPasswordAllowed", UNSET)

        edit_username_allowed = d.pop("editUsernameAllowed", UNSET)

        user_cache_enabled = d.pop("userCacheEnabled", UNSET)

        realm_cache_enabled = d.pop("realmCacheEnabled", UNSET)

        brute_force_protected = d.pop("bruteForceProtected", UNSET)

        permanent_lockout = d.pop("permanentLockout", UNSET)

        max_temporary_lockouts = d.pop("maxTemporaryLockouts", UNSET)

        _brute_force_strategy = d.pop("bruteForceStrategy", UNSET)
        brute_force_strategy: Union[Unset, BruteForceStrategy]
        if isinstance(_brute_force_strategy,  Unset):
            brute_force_strategy = UNSET
        else:
            brute_force_strategy = BruteForceStrategy(_brute_force_strategy)




        max_failure_wait_seconds = d.pop("maxFailureWaitSeconds", UNSET)

        minimum_quick_login_wait_seconds = d.pop("minimumQuickLoginWaitSeconds", UNSET)

        wait_increment_seconds = d.pop("waitIncrementSeconds", UNSET)

        quick_login_check_milli_seconds = d.pop("quickLoginCheckMilliSeconds", UNSET)

        max_delta_time_seconds = d.pop("maxDeltaTimeSeconds", UNSET)

        failure_factor = d.pop("failureFactor", UNSET)

        private_key = d.pop("privateKey", UNSET)

        public_key = d.pop("publicKey", UNSET)

        certificate = d.pop("certificate", UNSET)

        code_secret = d.pop("codeSecret", UNSET)

        _roles = d.pop("roles", UNSET)
        roles: Union[Unset, RolesRepresentation]
        if isinstance(_roles,  Unset):
            roles = UNSET
        else:
            roles = RolesRepresentation.from_dict(_roles)




        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in (_groups or []):
            groups_item = GroupRepresentation.from_dict(groups_item_data)



            groups.append(groups_item)


        default_roles = cast(list[str], d.pop("defaultRoles", UNSET))


        _default_role = d.pop("defaultRole", UNSET)
        default_role: Union[Unset, RoleRepresentation]
        if isinstance(_default_role,  Unset):
            default_role = UNSET
        else:
            default_role = RoleRepresentation.from_dict(_default_role)




        _admin_permissions_client = d.pop("adminPermissionsClient", UNSET)
        admin_permissions_client: Union[Unset, ClientRepresentation]
        if isinstance(_admin_permissions_client,  Unset):
            admin_permissions_client = UNSET
        else:
            admin_permissions_client = ClientRepresentation.from_dict(_admin_permissions_client)




        default_groups = cast(list[str], d.pop("defaultGroups", UNSET))


        required_credentials = cast(list[str], d.pop("requiredCredentials", UNSET))


        password_policy = d.pop("passwordPolicy", UNSET)

        otp_policy_type = d.pop("otpPolicyType", UNSET)

        otp_policy_algorithm = d.pop("otpPolicyAlgorithm", UNSET)

        otp_policy_initial_counter = d.pop("otpPolicyInitialCounter", UNSET)

        otp_policy_digits = d.pop("otpPolicyDigits", UNSET)

        otp_policy_look_ahead_window = d.pop("otpPolicyLookAheadWindow", UNSET)

        otp_policy_period = d.pop("otpPolicyPeriod", UNSET)

        otp_policy_code_reusable = d.pop("otpPolicyCodeReusable", UNSET)

        otp_supported_applications = cast(list[str], d.pop("otpSupportedApplications", UNSET))


        _localization_texts = d.pop("localizationTexts", UNSET)
        localization_texts: Union[Unset, RealmRepresentationLocalizationTexts]
        if isinstance(_localization_texts,  Unset):
            localization_texts = UNSET
        else:
            localization_texts = RealmRepresentationLocalizationTexts.from_dict(_localization_texts)




        web_authn_policy_rp_entity_name = d.pop("webAuthnPolicyRpEntityName", UNSET)

        web_authn_policy_signature_algorithms = cast(list[str], d.pop("webAuthnPolicySignatureAlgorithms", UNSET))


        web_authn_policy_rp_id = d.pop("webAuthnPolicyRpId", UNSET)

        web_authn_policy_attestation_conveyance_preference = d.pop("webAuthnPolicyAttestationConveyancePreference", UNSET)

        web_authn_policy_authenticator_attachment = d.pop("webAuthnPolicyAuthenticatorAttachment", UNSET)

        web_authn_policy_require_resident_key = d.pop("webAuthnPolicyRequireResidentKey", UNSET)

        web_authn_policy_user_verification_requirement = d.pop("webAuthnPolicyUserVerificationRequirement", UNSET)

        web_authn_policy_create_timeout = d.pop("webAuthnPolicyCreateTimeout", UNSET)

        web_authn_policy_avoid_same_authenticator_register = d.pop("webAuthnPolicyAvoidSameAuthenticatorRegister", UNSET)

        web_authn_policy_acceptable_aaguids = cast(list[str], d.pop("webAuthnPolicyAcceptableAaguids", UNSET))


        web_authn_policy_extra_origins = cast(list[str], d.pop("webAuthnPolicyExtraOrigins", UNSET))


        web_authn_policy_passwordless_rp_entity_name = d.pop("webAuthnPolicyPasswordlessRpEntityName", UNSET)

        web_authn_policy_passwordless_signature_algorithms = cast(list[str], d.pop("webAuthnPolicyPasswordlessSignatureAlgorithms", UNSET))


        web_authn_policy_passwordless_rp_id = d.pop("webAuthnPolicyPasswordlessRpId", UNSET)

        web_authn_policy_passwordless_attestation_conveyance_preference = d.pop("webAuthnPolicyPasswordlessAttestationConveyancePreference", UNSET)

        web_authn_policy_passwordless_authenticator_attachment = d.pop("webAuthnPolicyPasswordlessAuthenticatorAttachment", UNSET)

        web_authn_policy_passwordless_require_resident_key = d.pop("webAuthnPolicyPasswordlessRequireResidentKey", UNSET)

        web_authn_policy_passwordless_user_verification_requirement = d.pop("webAuthnPolicyPasswordlessUserVerificationRequirement", UNSET)

        web_authn_policy_passwordless_create_timeout = d.pop("webAuthnPolicyPasswordlessCreateTimeout", UNSET)

        web_authn_policy_passwordless_avoid_same_authenticator_register = d.pop("webAuthnPolicyPasswordlessAvoidSameAuthenticatorRegister", UNSET)

        web_authn_policy_passwordless_acceptable_aaguids = cast(list[str], d.pop("webAuthnPolicyPasswordlessAcceptableAaguids", UNSET))


        web_authn_policy_passwordless_extra_origins = cast(list[str], d.pop("webAuthnPolicyPasswordlessExtraOrigins", UNSET))


        web_authn_policy_passwordless_passkeys_enabled = d.pop("webAuthnPolicyPasswordlessPasskeysEnabled", UNSET)

        _client_profiles = d.pop("clientProfiles", UNSET)
        client_profiles: Union[Unset, ClientProfilesRepresentation]
        if isinstance(_client_profiles,  Unset):
            client_profiles = UNSET
        else:
            client_profiles = ClientProfilesRepresentation.from_dict(_client_profiles)




        _client_policies = d.pop("clientPolicies", UNSET)
        client_policies: Union[Unset, ClientPoliciesRepresentation]
        if isinstance(_client_policies,  Unset):
            client_policies = UNSET
        else:
            client_policies = ClientPoliciesRepresentation.from_dict(_client_policies)




        users = []
        _users = d.pop("users", UNSET)
        for users_item_data in (_users or []):
            users_item = UserRepresentation.from_dict(users_item_data)



            users.append(users_item)


        federated_users = []
        _federated_users = d.pop("federatedUsers", UNSET)
        for federated_users_item_data in (_federated_users or []):
            federated_users_item = UserRepresentation.from_dict(federated_users_item_data)



            federated_users.append(federated_users_item)


        scope_mappings = []
        _scope_mappings = d.pop("scopeMappings", UNSET)
        for scope_mappings_item_data in (_scope_mappings or []):
            scope_mappings_item = ScopeMappingRepresentation.from_dict(scope_mappings_item_data)



            scope_mappings.append(scope_mappings_item)


        _client_scope_mappings = d.pop("clientScopeMappings", UNSET)
        client_scope_mappings: Union[Unset, RealmRepresentationClientScopeMappings]
        if isinstance(_client_scope_mappings,  Unset):
            client_scope_mappings = UNSET
        else:
            client_scope_mappings = RealmRepresentationClientScopeMappings.from_dict(_client_scope_mappings)




        clients = []
        _clients = d.pop("clients", UNSET)
        for clients_item_data in (_clients or []):
            clients_item = ClientRepresentation.from_dict(clients_item_data)



            clients.append(clients_item)


        client_scopes = []
        _client_scopes = d.pop("clientScopes", UNSET)
        for client_scopes_item_data in (_client_scopes or []):
            client_scopes_item = ClientScopeRepresentation.from_dict(client_scopes_item_data)



            client_scopes.append(client_scopes_item)


        default_default_client_scopes = cast(list[str], d.pop("defaultDefaultClientScopes", UNSET))


        default_optional_client_scopes = cast(list[str], d.pop("defaultOptionalClientScopes", UNSET))


        _browser_security_headers = d.pop("browserSecurityHeaders", UNSET)
        browser_security_headers: Union[Unset, RealmRepresentationBrowserSecurityHeaders]
        if isinstance(_browser_security_headers,  Unset):
            browser_security_headers = UNSET
        else:
            browser_security_headers = RealmRepresentationBrowserSecurityHeaders.from_dict(_browser_security_headers)




        _smtp_server = d.pop("smtpServer", UNSET)
        smtp_server: Union[Unset, RealmRepresentationSmtpServer]
        if isinstance(_smtp_server,  Unset):
            smtp_server = UNSET
        else:
            smtp_server = RealmRepresentationSmtpServer.from_dict(_smtp_server)




        user_federation_providers = []
        _user_federation_providers = d.pop("userFederationProviders", UNSET)
        for user_federation_providers_item_data in (_user_federation_providers or []):
            user_federation_providers_item = UserFederationProviderRepresentation.from_dict(user_federation_providers_item_data)



            user_federation_providers.append(user_federation_providers_item)


        user_federation_mappers = []
        _user_federation_mappers = d.pop("userFederationMappers", UNSET)
        for user_federation_mappers_item_data in (_user_federation_mappers or []):
            user_federation_mappers_item = UserFederationMapperRepresentation.from_dict(user_federation_mappers_item_data)



            user_federation_mappers.append(user_federation_mappers_item)


        login_theme = d.pop("loginTheme", UNSET)

        account_theme = d.pop("accountTheme", UNSET)

        admin_theme = d.pop("adminTheme", UNSET)

        email_theme = d.pop("emailTheme", UNSET)

        events_enabled = d.pop("eventsEnabled", UNSET)

        events_expiration = d.pop("eventsExpiration", UNSET)

        events_listeners = cast(list[str], d.pop("eventsListeners", UNSET))


        enabled_event_types = cast(list[str], d.pop("enabledEventTypes", UNSET))


        admin_events_enabled = d.pop("adminEventsEnabled", UNSET)

        admin_events_details_enabled = d.pop("adminEventsDetailsEnabled", UNSET)

        identity_providers = []
        _identity_providers = d.pop("identityProviders", UNSET)
        for identity_providers_item_data in (_identity_providers or []):
            identity_providers_item = IdentityProviderRepresentation.from_dict(identity_providers_item_data)



            identity_providers.append(identity_providers_item)


        identity_provider_mappers = []
        _identity_provider_mappers = d.pop("identityProviderMappers", UNSET)
        for identity_provider_mappers_item_data in (_identity_provider_mappers or []):
            identity_provider_mappers_item = IdentityProviderMapperRepresentation.from_dict(identity_provider_mappers_item_data)



            identity_provider_mappers.append(identity_provider_mappers_item)


        protocol_mappers = []
        _protocol_mappers = d.pop("protocolMappers", UNSET)
        for protocol_mappers_item_data in (_protocol_mappers or []):
            protocol_mappers_item = ProtocolMapperRepresentation.from_dict(protocol_mappers_item_data)



            protocol_mappers.append(protocol_mappers_item)


        _components = d.pop("components", UNSET)
        components: Union[Unset, MultivaluedHashMapStringComponentExportRepresentation]
        if isinstance(_components,  Unset):
            components = UNSET
        else:
            components = MultivaluedHashMapStringComponentExportRepresentation.from_dict(_components)




        internationalization_enabled = d.pop("internationalizationEnabled", UNSET)

        supported_locales = cast(list[str], d.pop("supportedLocales", UNSET))


        default_locale = d.pop("defaultLocale", UNSET)

        authentication_flows = []
        _authentication_flows = d.pop("authenticationFlows", UNSET)
        for authentication_flows_item_data in (_authentication_flows or []):
            authentication_flows_item = AuthenticationFlowRepresentation.from_dict(authentication_flows_item_data)



            authentication_flows.append(authentication_flows_item)


        authenticator_config = []
        _authenticator_config = d.pop("authenticatorConfig", UNSET)
        for authenticator_config_item_data in (_authenticator_config or []):
            authenticator_config_item = AuthenticatorConfigRepresentation.from_dict(authenticator_config_item_data)



            authenticator_config.append(authenticator_config_item)


        required_actions = []
        _required_actions = d.pop("requiredActions", UNSET)
        for required_actions_item_data in (_required_actions or []):
            required_actions_item = RequiredActionProviderRepresentation.from_dict(required_actions_item_data)



            required_actions.append(required_actions_item)


        browser_flow = d.pop("browserFlow", UNSET)

        registration_flow = d.pop("registrationFlow", UNSET)

        direct_grant_flow = d.pop("directGrantFlow", UNSET)

        reset_credentials_flow = d.pop("resetCredentialsFlow", UNSET)

        client_authentication_flow = d.pop("clientAuthenticationFlow", UNSET)

        docker_authentication_flow = d.pop("dockerAuthenticationFlow", UNSET)

        first_broker_login_flow = d.pop("firstBrokerLoginFlow", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, RealmRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = RealmRepresentationAttributes.from_dict(_attributes)




        keycloak_version = d.pop("keycloakVersion", UNSET)

        user_managed_access_allowed = d.pop("userManagedAccessAllowed", UNSET)

        organizations_enabled = d.pop("organizationsEnabled", UNSET)

        organizations = []
        _organizations = d.pop("organizations", UNSET)
        for organizations_item_data in (_organizations or []):
            organizations_item = OrganizationRepresentation.from_dict(organizations_item_data)



            organizations.append(organizations_item)


        verifiable_credentials_enabled = d.pop("verifiableCredentialsEnabled", UNSET)

        admin_permissions_enabled = d.pop("adminPermissionsEnabled", UNSET)

        social = d.pop("social", UNSET)

        update_profile_on_initial_social_login = d.pop("updateProfileOnInitialSocialLogin", UNSET)

        _social_providers = d.pop("socialProviders", UNSET)
        social_providers: Union[Unset, RealmRepresentationSocialProviders]
        if isinstance(_social_providers,  Unset):
            social_providers = UNSET
        else:
            social_providers = RealmRepresentationSocialProviders.from_dict(_social_providers)




        _application_scope_mappings = d.pop("applicationScopeMappings", UNSET)
        application_scope_mappings: Union[Unset, RealmRepresentationApplicationScopeMappings]
        if isinstance(_application_scope_mappings,  Unset):
            application_scope_mappings = UNSET
        else:
            application_scope_mappings = RealmRepresentationApplicationScopeMappings.from_dict(_application_scope_mappings)




        applications = []
        _applications = d.pop("applications", UNSET)
        for applications_item_data in (_applications or []):
            applications_item = ApplicationRepresentation.from_dict(applications_item_data)



            applications.append(applications_item)


        oauth_clients = []
        _oauth_clients = d.pop("oauthClients", UNSET)
        for oauth_clients_item_data in (_oauth_clients or []):
            oauth_clients_item = OAuthClientRepresentation.from_dict(oauth_clients_item_data)



            oauth_clients.append(oauth_clients_item)


        client_templates = []
        _client_templates = d.pop("clientTemplates", UNSET)
        for client_templates_item_data in (_client_templates or []):
            client_templates_item = ClientTemplateRepresentation.from_dict(client_templates_item_data)



            client_templates.append(client_templates_item)


        o_auth_2_device_code_lifespan = d.pop("oAuth2DeviceCodeLifespan", UNSET)

        o_auth_2_device_polling_interval = d.pop("oAuth2DevicePollingInterval", UNSET)

        realm_representation = cls(
            id=id,
            realm=realm,
            display_name=display_name,
            display_name_html=display_name_html,
            not_before=not_before,
            default_signature_algorithm=default_signature_algorithm,
            revoke_refresh_token=revoke_refresh_token,
            refresh_token_max_reuse=refresh_token_max_reuse,
            access_token_lifespan=access_token_lifespan,
            access_token_lifespan_for_implicit_flow=access_token_lifespan_for_implicit_flow,
            sso_session_idle_timeout=sso_session_idle_timeout,
            sso_session_max_lifespan=sso_session_max_lifespan,
            sso_session_idle_timeout_remember_me=sso_session_idle_timeout_remember_me,
            sso_session_max_lifespan_remember_me=sso_session_max_lifespan_remember_me,
            offline_session_idle_timeout=offline_session_idle_timeout,
            offline_session_max_lifespan_enabled=offline_session_max_lifespan_enabled,
            offline_session_max_lifespan=offline_session_max_lifespan,
            client_session_idle_timeout=client_session_idle_timeout,
            client_session_max_lifespan=client_session_max_lifespan,
            client_offline_session_idle_timeout=client_offline_session_idle_timeout,
            client_offline_session_max_lifespan=client_offline_session_max_lifespan,
            access_code_lifespan=access_code_lifespan,
            access_code_lifespan_user_action=access_code_lifespan_user_action,
            access_code_lifespan_login=access_code_lifespan_login,
            action_token_generated_by_admin_lifespan=action_token_generated_by_admin_lifespan,
            action_token_generated_by_user_lifespan=action_token_generated_by_user_lifespan,
            oauth_2_device_code_lifespan=oauth_2_device_code_lifespan,
            oauth_2_device_polling_interval=oauth_2_device_polling_interval,
            enabled=enabled,
            ssl_required=ssl_required,
            password_credential_grant_allowed=password_credential_grant_allowed,
            registration_allowed=registration_allowed,
            registration_email_as_username=registration_email_as_username,
            remember_me=remember_me,
            verify_email=verify_email,
            login_with_email_allowed=login_with_email_allowed,
            duplicate_emails_allowed=duplicate_emails_allowed,
            reset_password_allowed=reset_password_allowed,
            edit_username_allowed=edit_username_allowed,
            user_cache_enabled=user_cache_enabled,
            realm_cache_enabled=realm_cache_enabled,
            brute_force_protected=brute_force_protected,
            permanent_lockout=permanent_lockout,
            max_temporary_lockouts=max_temporary_lockouts,
            brute_force_strategy=brute_force_strategy,
            max_failure_wait_seconds=max_failure_wait_seconds,
            minimum_quick_login_wait_seconds=minimum_quick_login_wait_seconds,
            wait_increment_seconds=wait_increment_seconds,
            quick_login_check_milli_seconds=quick_login_check_milli_seconds,
            max_delta_time_seconds=max_delta_time_seconds,
            failure_factor=failure_factor,
            private_key=private_key,
            public_key=public_key,
            certificate=certificate,
            code_secret=code_secret,
            roles=roles,
            groups=groups,
            default_roles=default_roles,
            default_role=default_role,
            admin_permissions_client=admin_permissions_client,
            default_groups=default_groups,
            required_credentials=required_credentials,
            password_policy=password_policy,
            otp_policy_type=otp_policy_type,
            otp_policy_algorithm=otp_policy_algorithm,
            otp_policy_initial_counter=otp_policy_initial_counter,
            otp_policy_digits=otp_policy_digits,
            otp_policy_look_ahead_window=otp_policy_look_ahead_window,
            otp_policy_period=otp_policy_period,
            otp_policy_code_reusable=otp_policy_code_reusable,
            otp_supported_applications=otp_supported_applications,
            localization_texts=localization_texts,
            web_authn_policy_rp_entity_name=web_authn_policy_rp_entity_name,
            web_authn_policy_signature_algorithms=web_authn_policy_signature_algorithms,
            web_authn_policy_rp_id=web_authn_policy_rp_id,
            web_authn_policy_attestation_conveyance_preference=web_authn_policy_attestation_conveyance_preference,
            web_authn_policy_authenticator_attachment=web_authn_policy_authenticator_attachment,
            web_authn_policy_require_resident_key=web_authn_policy_require_resident_key,
            web_authn_policy_user_verification_requirement=web_authn_policy_user_verification_requirement,
            web_authn_policy_create_timeout=web_authn_policy_create_timeout,
            web_authn_policy_avoid_same_authenticator_register=web_authn_policy_avoid_same_authenticator_register,
            web_authn_policy_acceptable_aaguids=web_authn_policy_acceptable_aaguids,
            web_authn_policy_extra_origins=web_authn_policy_extra_origins,
            web_authn_policy_passwordless_rp_entity_name=web_authn_policy_passwordless_rp_entity_name,
            web_authn_policy_passwordless_signature_algorithms=web_authn_policy_passwordless_signature_algorithms,
            web_authn_policy_passwordless_rp_id=web_authn_policy_passwordless_rp_id,
            web_authn_policy_passwordless_attestation_conveyance_preference=web_authn_policy_passwordless_attestation_conveyance_preference,
            web_authn_policy_passwordless_authenticator_attachment=web_authn_policy_passwordless_authenticator_attachment,
            web_authn_policy_passwordless_require_resident_key=web_authn_policy_passwordless_require_resident_key,
            web_authn_policy_passwordless_user_verification_requirement=web_authn_policy_passwordless_user_verification_requirement,
            web_authn_policy_passwordless_create_timeout=web_authn_policy_passwordless_create_timeout,
            web_authn_policy_passwordless_avoid_same_authenticator_register=web_authn_policy_passwordless_avoid_same_authenticator_register,
            web_authn_policy_passwordless_acceptable_aaguids=web_authn_policy_passwordless_acceptable_aaguids,
            web_authn_policy_passwordless_extra_origins=web_authn_policy_passwordless_extra_origins,
            web_authn_policy_passwordless_passkeys_enabled=web_authn_policy_passwordless_passkeys_enabled,
            client_profiles=client_profiles,
            client_policies=client_policies,
            users=users,
            federated_users=federated_users,
            scope_mappings=scope_mappings,
            client_scope_mappings=client_scope_mappings,
            clients=clients,
            client_scopes=client_scopes,
            default_default_client_scopes=default_default_client_scopes,
            default_optional_client_scopes=default_optional_client_scopes,
            browser_security_headers=browser_security_headers,
            smtp_server=smtp_server,
            user_federation_providers=user_federation_providers,
            user_federation_mappers=user_federation_mappers,
            login_theme=login_theme,
            account_theme=account_theme,
            admin_theme=admin_theme,
            email_theme=email_theme,
            events_enabled=events_enabled,
            events_expiration=events_expiration,
            events_listeners=events_listeners,
            enabled_event_types=enabled_event_types,
            admin_events_enabled=admin_events_enabled,
            admin_events_details_enabled=admin_events_details_enabled,
            identity_providers=identity_providers,
            identity_provider_mappers=identity_provider_mappers,
            protocol_mappers=protocol_mappers,
            components=components,
            internationalization_enabled=internationalization_enabled,
            supported_locales=supported_locales,
            default_locale=default_locale,
            authentication_flows=authentication_flows,
            authenticator_config=authenticator_config,
            required_actions=required_actions,
            browser_flow=browser_flow,
            registration_flow=registration_flow,
            direct_grant_flow=direct_grant_flow,
            reset_credentials_flow=reset_credentials_flow,
            client_authentication_flow=client_authentication_flow,
            docker_authentication_flow=docker_authentication_flow,
            first_broker_login_flow=first_broker_login_flow,
            attributes=attributes,
            keycloak_version=keycloak_version,
            user_managed_access_allowed=user_managed_access_allowed,
            organizations_enabled=organizations_enabled,
            organizations=organizations,
            verifiable_credentials_enabled=verifiable_credentials_enabled,
            admin_permissions_enabled=admin_permissions_enabled,
            social=social,
            update_profile_on_initial_social_login=update_profile_on_initial_social_login,
            social_providers=social_providers,
            application_scope_mappings=application_scope_mappings,
            applications=applications,
            oauth_clients=oauth_clients,
            client_templates=client_templates,
            o_auth_2_device_code_lifespan=o_auth_2_device_code_lifespan,
            o_auth_2_device_polling_interval=o_auth_2_device_polling_interval,
        )


        realm_representation.additional_properties = d
        return realm_representation

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
