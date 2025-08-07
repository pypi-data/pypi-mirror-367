"""
Keycloak API accessor classes.

These classes provide a clean interface over the generated API code.
"""
from .base import *
from .users import *
from .realms import *
from .clients import *
from .roles import *
from .groups import *
from .organizations import *
from .identity_providers import *
from .client_scopes import *
from .components import *
from .sessions import *
from .events import *
from .authentication import *
from .authorization import *
from .protocol_mappers import *
from .keys import *
from .scope_mappings import *
from .client_role_mappings import *
from .role_mapper import *
from .roles_by_id import *
from .attack_detection import *
from .client_initial_access import *
from .client_attribute_certificate import *
from .client_registration_policy import *

__all__ = (
    "AuthError", "APIError", "AuthenticatedClient", "Client", "BaseAPI", "BaseClientManager",
    "UsersAPI", "UsersClientMixin", "UserRepresentation", "CredentialRepresentation", "UserConsentRepresentation", "FederatedIdentityRepresentation",
    "RealmsAPI", "RealmsClientMixin", "RealmRepresentation",
    "ClientsAPI", "ClientsClientMixin", "ClientRepresentation", "ManagementPermissionReference",
    "RolesAPI", "RolesClientMixin", "RoleRepresentation",
    "GroupsAPI", "GroupsClientMixin", "GroupRepresentation",
    "OrganizationsAPI", "OrganizationsClientMixin", "OrganizationRepresentation",
    "IdentityProvidersAPI", "IdentityProvidersClientMixin", "IdentityProviderRepresentation",
    "ClientScopesAPI", "ClientScopesClientMixin", "ClientScopeRepresentation", "GlobalRequestResult",
    "ComponentsAPI", "ComponentsClientMixin", "ComponentRepresentation", "ComponentTypeRepresentation",
    "SessionsAPI", "SessionsClientMixin", "UserSessionRepresentation",
    "EventsAPI", "EventsClientMixin", "RealmEventsConfigRepresentation", "EventRepresentation", "AdminEventRepresentation",
    "AuthenticationAPI", "AuthenticationClientMixin", "AuthenticationFlowRepresentation", "AuthenticationExecutionInfoRepresentation", "AuthenticatorConfigRepresentation", "RequiredActionProviderRepresentation",
    "AuthorizationAPI", "AuthorizationClientMixin", "ResourceServerRepresentation", "ResourceRepresentation", "ScopeRepresentation", "AbstractPolicyRepresentation", "PolicyProviderRepresentation", "PolicyEvaluationResponse", "EvaluationResultRepresentation", "PolicyRepresentation",
    "ProtocolMappersAPI", "ProtocolMappersClientMixin", "ProtocolMapperRepresentation",
    "KeysAPI", "KeysClientMixin", "KeysMetadataRepresentation",
    "ScopeMappingsAPI", "ScopeMappingsClientMixin",
    "ClientRoleMappingsAPI", "ClientRoleMappingsClientMixin",
    "RoleMapperAPI", "RoleMapperClientMixin",
    "RolesByIdAPI", "RolesByIdClientMixin",
    "AttackDetectionAPI", "AttackDetectionClientMixin",
    "ClientInitialAccessAPI", "ClientInitialAccessClientMixin", "ClientInitialAccessPresentation", "ClientInitialAccessCreatePresentation",
    "ClientAttributeCertificateAPI", "ClientAttributeCertificateClientMixin", "CertificateRepresentation", "KeyStoreConfig",
    "ClientRegistrationPolicyAPI", "ClientRegistrationPolicyClientMixin",
    "KeycloakClientMixin",
)


class KeycloakClientMixin(
    UsersClientMixin,
    RealmsClientMixin,
    ClientsClientMixin,
    RolesClientMixin,
    GroupsClientMixin,
    OrganizationsClientMixin,
    IdentityProvidersClientMixin,
    ClientScopesClientMixin,
    ComponentsClientMixin,
    SessionsClientMixin,
    EventsClientMixin,
    AuthenticationClientMixin,
    AuthorizationClientMixin,
    ProtocolMappersClientMixin,
    KeysClientMixin,
    ScopeMappingsClientMixin,
    ClientRoleMappingsClientMixin,
    RoleMapperClientMixin,
    RolesByIdClientMixin,
    AttackDetectionClientMixin,
    ClientInitialAccessClientMixin,
    ClientAttributeCertificateClientMixin,
    ClientRegistrationPolicyClientMixin,
):
    """
    Mixin that provides all Keycloak API methods in a single class.

    This allows using the Keycloak client without needing to instantiate
    separate API classes.

    Classes using this should also inherit from BaseKeycloakClient or BaseClientManager.
    """
