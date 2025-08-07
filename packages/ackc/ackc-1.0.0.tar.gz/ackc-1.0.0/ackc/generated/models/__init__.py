""" Contains all the data models used in inputs/outputs """

from .abstract_policy_representation import AbstractPolicyRepresentation
from .access import Access
from .access_token import AccessToken
from .access_token_other_claims import AccessTokenOtherClaims
from .access_token_resource_access import AccessTokenResourceAccess
from .address_claim_set import AddressClaimSet
from .admin_event_representation import AdminEventRepresentation
from .admin_event_representation_details import AdminEventRepresentationDetails
from .application_representation import ApplicationRepresentation
from .application_representation_access import ApplicationRepresentationAccess
from .application_representation_attributes import ApplicationRepresentationAttributes
from .application_representation_authentication_flow_binding_overrides import ApplicationRepresentationAuthenticationFlowBindingOverrides
from .application_representation_registered_nodes import ApplicationRepresentationRegisteredNodes
from .auth_details_representation import AuthDetailsRepresentation
from .authentication_execution_export_representation import AuthenticationExecutionExportRepresentation
from .authentication_execution_info_representation import AuthenticationExecutionInfoRepresentation
from .authentication_execution_representation import AuthenticationExecutionRepresentation
from .authentication_flow_representation import AuthenticationFlowRepresentation
from .authenticator_config_info_representation import AuthenticatorConfigInfoRepresentation
from .authenticator_config_representation import AuthenticatorConfigRepresentation
from .authenticator_config_representation_config import AuthenticatorConfigRepresentationConfig
from .authorization import Authorization
from .authorization_schema import AuthorizationSchema
from .authorization_schema_resource_types import AuthorizationSchemaResourceTypes
from .brute_force_strategy import BruteForceStrategy
from .certificate_representation import CertificateRepresentation
from .claim_representation import ClaimRepresentation
from .client_initial_access_create_presentation import ClientInitialAccessCreatePresentation
from .client_initial_access_presentation import ClientInitialAccessPresentation
from .client_mappings_representation import ClientMappingsRepresentation
from .client_policies_representation import ClientPoliciesRepresentation
from .client_policy_condition_representation import ClientPolicyConditionRepresentation
from .client_policy_condition_representation_configuration import ClientPolicyConditionRepresentationConfiguration
from .client_policy_executor_representation import ClientPolicyExecutorRepresentation
from .client_policy_executor_representation_configuration import ClientPolicyExecutorRepresentationConfiguration
from .client_policy_representation import ClientPolicyRepresentation
from .client_profile_representation import ClientProfileRepresentation
from .client_profiles_representation import ClientProfilesRepresentation
from .client_representation import ClientRepresentation
from .client_representation_access import ClientRepresentationAccess
from .client_representation_attributes import ClientRepresentationAttributes
from .client_representation_authentication_flow_binding_overrides import ClientRepresentationAuthenticationFlowBindingOverrides
from .client_representation_registered_nodes import ClientRepresentationRegisteredNodes
from .client_scope_representation import ClientScopeRepresentation
from .client_scope_representation_attributes import ClientScopeRepresentationAttributes
from .client_template_representation import ClientTemplateRepresentation
from .client_template_representation_attributes import ClientTemplateRepresentationAttributes
from .client_type_representation import ClientTypeRepresentation
from .client_type_representation_config import ClientTypeRepresentationConfig
from .client_types_representation import ClientTypesRepresentation
from .component_export_representation import ComponentExportRepresentation
from .component_representation import ComponentRepresentation
from .component_type_representation import ComponentTypeRepresentation
from .component_type_representation_metadata import ComponentTypeRepresentationMetadata
from .composites import Composites
from .composites_application import CompositesApplication
from .composites_client import CompositesClient
from .config_property_representation import ConfigPropertyRepresentation
from .confirmation import Confirmation
from .credential_representation import CredentialRepresentation
from .decision_effect import DecisionEffect
from .decision_strategy import DecisionStrategy
from .enforcement_mode import EnforcementMode
from .error_representation import ErrorRepresentation
from .evaluation_result_representation import EvaluationResultRepresentation
from .event_representation import EventRepresentation
from .event_representation_details import EventRepresentationDetails
from .federated_identity_representation import FederatedIdentityRepresentation
from .get_admin_realms_realm_attack_detection_brute_force_users_user_id_response_200 import GetAdminRealmsRealmAttackDetectionBruteForceUsersUserIdResponse200
from .get_admin_realms_realm_authentication_authenticator_providers_response_200_item import GetAdminRealmsRealmAuthenticationAuthenticatorProvidersResponse200Item
from .get_admin_realms_realm_authentication_client_authenticator_providers_response_200_item import GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item
from .get_admin_realms_realm_authentication_form_action_providers_response_200_item import GetAdminRealmsRealmAuthenticationFormActionProvidersResponse200Item
from .get_admin_realms_realm_authentication_form_providers_response_200_item import GetAdminRealmsRealmAuthenticationFormProvidersResponse200Item
from .get_admin_realms_realm_authentication_per_client_config_description_response_200 import GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200
from .get_admin_realms_realm_authentication_unregistered_required_actions_response_200_item import GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item
from .get_admin_realms_realm_client_session_stats_response_200_item import GetAdminRealmsRealmClientSessionStatsResponse200Item
from .get_admin_realms_realm_clients_client_uuid_evaluate_scopes_generate_example_userinfo_response_200 import GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200
from .get_admin_realms_realm_clients_client_uuid_offline_session_count_response_200 import GetAdminRealmsRealmClientsClientUuidOfflineSessionCountResponse200
from .get_admin_realms_realm_clients_client_uuid_session_count_response_200 import GetAdminRealmsRealmClientsClientUuidSessionCountResponse200
from .get_admin_realms_realm_groups_count_response_200 import GetAdminRealmsRealmGroupsCountResponse200
from .get_admin_realms_realm_identity_provider_providers_provider_id_response_200 import GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200
from .get_admin_realms_realm_localization_locale_response_200 import GetAdminRealmsRealmLocalizationLocaleResponse200
from .get_admin_realms_realm_users_user_id_consents_response_200_item import GetAdminRealmsRealmUsersUserIdConsentsResponse200Item
from .get_admin_realms_realm_users_user_id_groups_count_response_200 import GetAdminRealmsRealmUsersUserIdGroupsCountResponse200
from .get_admin_realms_realm_users_user_id_unmanaged_attributes_response_200 import GetAdminRealmsRealmUsersUserIdUnmanagedAttributesResponse200
from .global_request_result import GlobalRequestResult
from .group_representation import GroupRepresentation
from .group_representation_access import GroupRepresentationAccess
from .group_representation_attributes import GroupRepresentationAttributes
from .group_representation_client_roles import GroupRepresentationClientRoles
from .id_token import IDToken
from .id_token_other_claims import IDTokenOtherClaims
from .identity_provider_mapper_representation import IdentityProviderMapperRepresentation
from .identity_provider_mapper_representation_config import IdentityProviderMapperRepresentationConfig
from .identity_provider_mapper_type_representation import IdentityProviderMapperTypeRepresentation
from .identity_provider_representation import IdentityProviderRepresentation
from .identity_provider_representation_config import IdentityProviderRepresentationConfig
from .installation_adapter_config import InstallationAdapterConfig
from .installation_adapter_config_credentials import InstallationAdapterConfigCredentials
from .key_metadata_representation import KeyMetadataRepresentation
from .key_store_config import KeyStoreConfig
from .key_use import KeyUse
from .keys_metadata_representation import KeysMetadataRepresentation
from .keys_metadata_representation_active import KeysMetadataRepresentationActive
from .logic import Logic
from .management_permission_reference import ManagementPermissionReference
from .management_permission_reference_scope_permissions import ManagementPermissionReferenceScopePermissions
from .mappings_representation import MappingsRepresentation
from .mappings_representation_client_mappings import MappingsRepresentationClientMappings
from .member_representation import MemberRepresentation
from .member_representation_access import MemberRepresentationAccess
from .member_representation_application_roles import MemberRepresentationApplicationRoles
from .member_representation_attributes import MemberRepresentationAttributes
from .member_representation_client_roles import MemberRepresentationClientRoles
from .membership_type import MembershipType
from .method_config import MethodConfig
from .multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
from .multivalued_hash_map_string_string import MultivaluedHashMapStringString
from .o_auth_client_representation import OAuthClientRepresentation
from .o_auth_client_representation_access import OAuthClientRepresentationAccess
from .o_auth_client_representation_attributes import OAuthClientRepresentationAttributes
from .o_auth_client_representation_authentication_flow_binding_overrides import OAuthClientRepresentationAuthenticationFlowBindingOverrides
from .o_auth_client_representation_registered_nodes import OAuthClientRepresentationRegisteredNodes
from .organization_domain_representation import OrganizationDomainRepresentation
from .organization_representation import OrganizationRepresentation
from .organization_representation_attributes import OrganizationRepresentationAttributes
from .path_cache_config import PathCacheConfig
from .path_config import PathConfig
from .path_config_claim_information_point import PathConfigClaimInformationPoint
from .path_config_claim_information_point_additional_property import PathConfigClaimInformationPointAdditionalProperty
from .permission import Permission
from .permission_claims import PermissionClaims
from .policy_enforcement_mode import PolicyEnforcementMode
from .policy_enforcer_config import PolicyEnforcerConfig
from .policy_enforcer_config_claim_information_point import PolicyEnforcerConfigClaimInformationPoint
from .policy_enforcer_config_claim_information_point_additional_property import PolicyEnforcerConfigClaimInformationPointAdditionalProperty
from .policy_enforcer_config_credentials import PolicyEnforcerConfigCredentials
from .policy_evaluation_request import PolicyEvaluationRequest
from .policy_evaluation_request_context import PolicyEvaluationRequestContext
from .policy_evaluation_request_context_additional_property import PolicyEvaluationRequestContextAdditionalProperty
from .policy_evaluation_response import PolicyEvaluationResponse
from .policy_provider_representation import PolicyProviderRepresentation
from .policy_representation import PolicyRepresentation
from .policy_representation_config import PolicyRepresentationConfig
from .policy_result_representation import PolicyResultRepresentation
from .post_admin_realms_realm_authentication_flows_flow_alias_copy_body import PostAdminRealmsRealmAuthenticationFlowsFlowAliasCopyBody
from .post_admin_realms_realm_authentication_flows_flow_alias_executions_execution_body import PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsExecutionBody
from .post_admin_realms_realm_authentication_flows_flow_alias_executions_flow_body import PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsFlowBody
from .post_admin_realms_realm_authentication_register_required_action_body import PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody
from .post_admin_realms_realm_clients_client_uuid_nodes_body import PostAdminRealmsRealmClientsClientUuidNodesBody
from .post_admin_realms_realm_identity_provider_import_config_body import PostAdminRealmsRealmIdentityProviderImportConfigBody
from .post_admin_realms_realm_identity_provider_import_config_response_200 import PostAdminRealmsRealmIdentityProviderImportConfigResponse200
from .post_admin_realms_realm_localization_locale_body import PostAdminRealmsRealmLocalizationLocaleBody
from .post_admin_realms_realm_organizations_org_id_members_invite_existing_user_body import PostAdminRealmsRealmOrganizationsOrgIdMembersInviteExistingUserBody
from .post_admin_realms_realm_organizations_org_id_members_invite_user_body import PostAdminRealmsRealmOrganizationsOrgIdMembersInviteUserBody
from .post_admin_realms_realm_partial_import_response_200 import PostAdminRealmsRealmPartialImportResponse200
from .post_admin_realms_realm_test_smtp_connection_data_body import PostAdminRealmsRealmTestSMTPConnectionDataBody
from .post_admin_realms_realm_test_smtp_connection_json_body import PostAdminRealmsRealmTestSMTPConnectionJsonBody
from .post_admin_realms_realm_users_user_id_impersonation_response_200 import PostAdminRealmsRealmUsersUserIdImpersonationResponse200
from .property_config import PropertyConfig
from .protocol_mapper_evaluation_representation import ProtocolMapperEvaluationRepresentation
from .protocol_mapper_representation import ProtocolMapperRepresentation
from .protocol_mapper_representation_config import ProtocolMapperRepresentationConfig
from .published_realm_representation import PublishedRealmRepresentation
from .realm_events_config_representation import RealmEventsConfigRepresentation
from .realm_representation import RealmRepresentation
from .realm_representation_application_scope_mappings import RealmRepresentationApplicationScopeMappings
from .realm_representation_attributes import RealmRepresentationAttributes
from .realm_representation_browser_security_headers import RealmRepresentationBrowserSecurityHeaders
from .realm_representation_client_scope_mappings import RealmRepresentationClientScopeMappings
from .realm_representation_localization_texts import RealmRepresentationLocalizationTexts
from .realm_representation_localization_texts_additional_property import RealmRepresentationLocalizationTextsAdditionalProperty
from .realm_representation_smtp_server import RealmRepresentationSmtpServer
from .realm_representation_social_providers import RealmRepresentationSocialProviders
from .required_action_config_info_representation import RequiredActionConfigInfoRepresentation
from .required_action_config_representation import RequiredActionConfigRepresentation
from .required_action_config_representation_config import RequiredActionConfigRepresentationConfig
from .required_action_provider_representation import RequiredActionProviderRepresentation
from .required_action_provider_representation_config import RequiredActionProviderRepresentationConfig
from .resource_owner_representation import ResourceOwnerRepresentation
from .resource_representation import ResourceRepresentation
from .resource_representation_attributes import ResourceRepresentationAttributes
from .resource_server_representation import ResourceServerRepresentation
from .resource_type import ResourceType
from .resource_type_scope_aliases import ResourceTypeScopeAliases
from .role_representation import RoleRepresentation
from .role_representation_attributes import RoleRepresentationAttributes
from .roles_representation import RolesRepresentation
from .roles_representation_application import RolesRepresentationApplication
from .roles_representation_client import RolesRepresentationClient
from .scope_enforcement_mode import ScopeEnforcementMode
from .scope_mapping_representation import ScopeMappingRepresentation
from .scope_representation import ScopeRepresentation
from .social_link_representation import SocialLinkRepresentation
from .unmanaged_attribute_policy import UnmanagedAttributePolicy
from .up_attribute import UPAttribute
from .up_attribute_annotations import UPAttributeAnnotations
from .up_attribute_permissions import UPAttributePermissions
from .up_attribute_required import UPAttributeRequired
from .up_attribute_selector import UPAttributeSelector
from .up_attribute_validations import UPAttributeValidations
from .up_attribute_validations_additional_property import UPAttributeValidationsAdditionalProperty
from .up_config import UPConfig
from .up_group import UPGroup
from .up_group_annotations import UPGroupAnnotations
from .user_consent_representation import UserConsentRepresentation
from .user_federation_mapper_representation import UserFederationMapperRepresentation
from .user_federation_mapper_representation_config import UserFederationMapperRepresentationConfig
from .user_federation_provider_representation import UserFederationProviderRepresentation
from .user_federation_provider_representation_config import UserFederationProviderRepresentationConfig
from .user_managed_access_config import UserManagedAccessConfig
from .user_profile_attribute_group_metadata import UserProfileAttributeGroupMetadata
from .user_profile_attribute_group_metadata_annotations import UserProfileAttributeGroupMetadataAnnotations
from .user_profile_attribute_metadata import UserProfileAttributeMetadata
from .user_profile_attribute_metadata_annotations import UserProfileAttributeMetadataAnnotations
from .user_profile_attribute_metadata_validators import UserProfileAttributeMetadataValidators
from .user_profile_attribute_metadata_validators_additional_property import UserProfileAttributeMetadataValidatorsAdditionalProperty
from .user_profile_metadata import UserProfileMetadata
from .user_representation import UserRepresentation
from .user_representation_access import UserRepresentationAccess
from .user_representation_application_roles import UserRepresentationApplicationRoles
from .user_representation_attributes import UserRepresentationAttributes
from .user_representation_client_roles import UserRepresentationClientRoles
from .user_session_representation import UserSessionRepresentation
from .user_session_representation_clients import UserSessionRepresentationClients

__all__ = (
    "AbstractPolicyRepresentation",
    "Access",
    "AccessToken",
    "AccessTokenOtherClaims",
    "AccessTokenResourceAccess",
    "AddressClaimSet",
    "AdminEventRepresentation",
    "AdminEventRepresentationDetails",
    "ApplicationRepresentation",
    "ApplicationRepresentationAccess",
    "ApplicationRepresentationAttributes",
    "ApplicationRepresentationAuthenticationFlowBindingOverrides",
    "ApplicationRepresentationRegisteredNodes",
    "AuthDetailsRepresentation",
    "AuthenticationExecutionExportRepresentation",
    "AuthenticationExecutionInfoRepresentation",
    "AuthenticationExecutionRepresentation",
    "AuthenticationFlowRepresentation",
    "AuthenticatorConfigInfoRepresentation",
    "AuthenticatorConfigRepresentation",
    "AuthenticatorConfigRepresentationConfig",
    "Authorization",
    "AuthorizationSchema",
    "AuthorizationSchemaResourceTypes",
    "BruteForceStrategy",
    "CertificateRepresentation",
    "ClaimRepresentation",
    "ClientInitialAccessCreatePresentation",
    "ClientInitialAccessPresentation",
    "ClientMappingsRepresentation",
    "ClientPoliciesRepresentation",
    "ClientPolicyConditionRepresentation",
    "ClientPolicyConditionRepresentationConfiguration",
    "ClientPolicyExecutorRepresentation",
    "ClientPolicyExecutorRepresentationConfiguration",
    "ClientPolicyRepresentation",
    "ClientProfileRepresentation",
    "ClientProfilesRepresentation",
    "ClientRepresentation",
    "ClientRepresentationAccess",
    "ClientRepresentationAttributes",
    "ClientRepresentationAuthenticationFlowBindingOverrides",
    "ClientRepresentationRegisteredNodes",
    "ClientScopeRepresentation",
    "ClientScopeRepresentationAttributes",
    "ClientTemplateRepresentation",
    "ClientTemplateRepresentationAttributes",
    "ClientTypeRepresentation",
    "ClientTypeRepresentationConfig",
    "ClientTypesRepresentation",
    "ComponentExportRepresentation",
    "ComponentRepresentation",
    "ComponentTypeRepresentation",
    "ComponentTypeRepresentationMetadata",
    "Composites",
    "CompositesApplication",
    "CompositesClient",
    "ConfigPropertyRepresentation",
    "Confirmation",
    "CredentialRepresentation",
    "DecisionEffect",
    "DecisionStrategy",
    "EnforcementMode",
    "ErrorRepresentation",
    "EvaluationResultRepresentation",
    "EventRepresentation",
    "EventRepresentationDetails",
    "FederatedIdentityRepresentation",
    "GetAdminRealmsRealmAttackDetectionBruteForceUsersUserIdResponse200",
    "GetAdminRealmsRealmAuthenticationAuthenticatorProvidersResponse200Item",
    "GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item",
    "GetAdminRealmsRealmAuthenticationFormActionProvidersResponse200Item",
    "GetAdminRealmsRealmAuthenticationFormProvidersResponse200Item",
    "GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200",
    "GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item",
    "GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200",
    "GetAdminRealmsRealmClientsClientUuidOfflineSessionCountResponse200",
    "GetAdminRealmsRealmClientsClientUuidSessionCountResponse200",
    "GetAdminRealmsRealmClientSessionStatsResponse200Item",
    "GetAdminRealmsRealmGroupsCountResponse200",
    "GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200",
    "GetAdminRealmsRealmLocalizationLocaleResponse200",
    "GetAdminRealmsRealmUsersUserIdConsentsResponse200Item",
    "GetAdminRealmsRealmUsersUserIdGroupsCountResponse200",
    "GetAdminRealmsRealmUsersUserIdUnmanagedAttributesResponse200",
    "GlobalRequestResult",
    "GroupRepresentation",
    "GroupRepresentationAccess",
    "GroupRepresentationAttributes",
    "GroupRepresentationClientRoles",
    "IdentityProviderMapperRepresentation",
    "IdentityProviderMapperRepresentationConfig",
    "IdentityProviderMapperTypeRepresentation",
    "IdentityProviderRepresentation",
    "IdentityProviderRepresentationConfig",
    "IDToken",
    "IDTokenOtherClaims",
    "InstallationAdapterConfig",
    "InstallationAdapterConfigCredentials",
    "KeyMetadataRepresentation",
    "KeysMetadataRepresentation",
    "KeysMetadataRepresentationActive",
    "KeyStoreConfig",
    "KeyUse",
    "Logic",
    "ManagementPermissionReference",
    "ManagementPermissionReferenceScopePermissions",
    "MappingsRepresentation",
    "MappingsRepresentationClientMappings",
    "MemberRepresentation",
    "MemberRepresentationAccess",
    "MemberRepresentationApplicationRoles",
    "MemberRepresentationAttributes",
    "MemberRepresentationClientRoles",
    "MembershipType",
    "MethodConfig",
    "MultivaluedHashMapStringComponentExportRepresentation",
    "MultivaluedHashMapStringString",
    "OAuthClientRepresentation",
    "OAuthClientRepresentationAccess",
    "OAuthClientRepresentationAttributes",
    "OAuthClientRepresentationAuthenticationFlowBindingOverrides",
    "OAuthClientRepresentationRegisteredNodes",
    "OrganizationDomainRepresentation",
    "OrganizationRepresentation",
    "OrganizationRepresentationAttributes",
    "PathCacheConfig",
    "PathConfig",
    "PathConfigClaimInformationPoint",
    "PathConfigClaimInformationPointAdditionalProperty",
    "Permission",
    "PermissionClaims",
    "PolicyEnforcementMode",
    "PolicyEnforcerConfig",
    "PolicyEnforcerConfigClaimInformationPoint",
    "PolicyEnforcerConfigClaimInformationPointAdditionalProperty",
    "PolicyEnforcerConfigCredentials",
    "PolicyEvaluationRequest",
    "PolicyEvaluationRequestContext",
    "PolicyEvaluationRequestContextAdditionalProperty",
    "PolicyEvaluationResponse",
    "PolicyProviderRepresentation",
    "PolicyRepresentation",
    "PolicyRepresentationConfig",
    "PolicyResultRepresentation",
    "PostAdminRealmsRealmAuthenticationFlowsFlowAliasCopyBody",
    "PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsExecutionBody",
    "PostAdminRealmsRealmAuthenticationFlowsFlowAliasExecutionsFlowBody",
    "PostAdminRealmsRealmAuthenticationRegisterRequiredActionBody",
    "PostAdminRealmsRealmClientsClientUuidNodesBody",
    "PostAdminRealmsRealmIdentityProviderImportConfigBody",
    "PostAdminRealmsRealmIdentityProviderImportConfigResponse200",
    "PostAdminRealmsRealmLocalizationLocaleBody",
    "PostAdminRealmsRealmOrganizationsOrgIdMembersInviteExistingUserBody",
    "PostAdminRealmsRealmOrganizationsOrgIdMembersInviteUserBody",
    "PostAdminRealmsRealmPartialImportResponse200",
    "PostAdminRealmsRealmTestSMTPConnectionDataBody",
    "PostAdminRealmsRealmTestSMTPConnectionJsonBody",
    "PostAdminRealmsRealmUsersUserIdImpersonationResponse200",
    "PropertyConfig",
    "ProtocolMapperEvaluationRepresentation",
    "ProtocolMapperRepresentation",
    "ProtocolMapperRepresentationConfig",
    "PublishedRealmRepresentation",
    "RealmEventsConfigRepresentation",
    "RealmRepresentation",
    "RealmRepresentationApplicationScopeMappings",
    "RealmRepresentationAttributes",
    "RealmRepresentationBrowserSecurityHeaders",
    "RealmRepresentationClientScopeMappings",
    "RealmRepresentationLocalizationTexts",
    "RealmRepresentationLocalizationTextsAdditionalProperty",
    "RealmRepresentationSmtpServer",
    "RealmRepresentationSocialProviders",
    "RequiredActionConfigInfoRepresentation",
    "RequiredActionConfigRepresentation",
    "RequiredActionConfigRepresentationConfig",
    "RequiredActionProviderRepresentation",
    "RequiredActionProviderRepresentationConfig",
    "ResourceOwnerRepresentation",
    "ResourceRepresentation",
    "ResourceRepresentationAttributes",
    "ResourceServerRepresentation",
    "ResourceType",
    "ResourceTypeScopeAliases",
    "RoleRepresentation",
    "RoleRepresentationAttributes",
    "RolesRepresentation",
    "RolesRepresentationApplication",
    "RolesRepresentationClient",
    "ScopeEnforcementMode",
    "ScopeMappingRepresentation",
    "ScopeRepresentation",
    "SocialLinkRepresentation",
    "UnmanagedAttributePolicy",
    "UPAttribute",
    "UPAttributeAnnotations",
    "UPAttributePermissions",
    "UPAttributeRequired",
    "UPAttributeSelector",
    "UPAttributeValidations",
    "UPAttributeValidationsAdditionalProperty",
    "UPConfig",
    "UPGroup",
    "UPGroupAnnotations",
    "UserConsentRepresentation",
    "UserFederationMapperRepresentation",
    "UserFederationMapperRepresentationConfig",
    "UserFederationProviderRepresentation",
    "UserFederationProviderRepresentationConfig",
    "UserManagedAccessConfig",
    "UserProfileAttributeGroupMetadata",
    "UserProfileAttributeGroupMetadataAnnotations",
    "UserProfileAttributeMetadata",
    "UserProfileAttributeMetadataAnnotations",
    "UserProfileAttributeMetadataValidators",
    "UserProfileAttributeMetadataValidatorsAdditionalProperty",
    "UserProfileMetadata",
    "UserRepresentation",
    "UserRepresentationAccess",
    "UserRepresentationApplicationRoles",
    "UserRepresentationAttributes",
    "UserRepresentationClientRoles",
    "UserSessionRepresentation",
    "UserSessionRepresentationClients",
)
