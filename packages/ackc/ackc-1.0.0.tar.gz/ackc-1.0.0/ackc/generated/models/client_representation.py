from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_representation_registered_nodes import ClientRepresentationRegisteredNodes
  from ..models.resource_server_representation import ResourceServerRepresentation
  from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
  from ..models.client_representation_authentication_flow_binding_overrides import ClientRepresentationAuthenticationFlowBindingOverrides
  from ..models.client_representation_attributes import ClientRepresentationAttributes
  from ..models.client_representation_access import ClientRepresentationAccess





T = TypeVar("T", bound="ClientRepresentation")



@_attrs_define
class ClientRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            client_id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            type_ (Union[Unset, str]):
            root_url (Union[Unset, str]):
            admin_url (Union[Unset, str]):
            base_url (Union[Unset, str]):
            surrogate_auth_required (Union[Unset, bool]):
            enabled (Union[Unset, bool]):
            always_display_in_console (Union[Unset, bool]):
            client_authenticator_type (Union[Unset, str]):
            secret (Union[Unset, str]):
            registration_access_token (Union[Unset, str]):
            default_roles (Union[Unset, list[str]]):
            redirect_uris (Union[Unset, list[str]]):
            web_origins (Union[Unset, list[str]]):
            not_before (Union[Unset, int]):
            bearer_only (Union[Unset, bool]):
            consent_required (Union[Unset, bool]):
            standard_flow_enabled (Union[Unset, bool]):
            implicit_flow_enabled (Union[Unset, bool]):
            direct_access_grants_enabled (Union[Unset, bool]):
            service_accounts_enabled (Union[Unset, bool]):
            authorization_services_enabled (Union[Unset, bool]):
            direct_grants_only (Union[Unset, bool]):
            public_client (Union[Unset, bool]):
            frontchannel_logout (Union[Unset, bool]):
            protocol (Union[Unset, str]):
            attributes (Union[Unset, ClientRepresentationAttributes]):
            authentication_flow_binding_overrides (Union[Unset, ClientRepresentationAuthenticationFlowBindingOverrides]):
            full_scope_allowed (Union[Unset, bool]):
            node_re_registration_timeout (Union[Unset, int]):
            registered_nodes (Union[Unset, ClientRepresentationRegisteredNodes]):
            protocol_mappers (Union[Unset, list['ProtocolMapperRepresentation']]):
            client_template (Union[Unset, str]):
            use_template_config (Union[Unset, bool]):
            use_template_scope (Union[Unset, bool]):
            use_template_mappers (Union[Unset, bool]):
            default_client_scopes (Union[Unset, list[str]]):
            optional_client_scopes (Union[Unset, list[str]]):
            authorization_settings (Union[Unset, ResourceServerRepresentation]):
            access (Union[Unset, ClientRepresentationAccess]):
            origin (Union[Unset, str]):
     """

    id: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    root_url: Union[Unset, str] = UNSET
    admin_url: Union[Unset, str] = UNSET
    base_url: Union[Unset, str] = UNSET
    surrogate_auth_required: Union[Unset, bool] = UNSET
    enabled: Union[Unset, bool] = UNSET
    always_display_in_console: Union[Unset, bool] = UNSET
    client_authenticator_type: Union[Unset, str] = UNSET
    secret: Union[Unset, str] = UNSET
    registration_access_token: Union[Unset, str] = UNSET
    default_roles: Union[Unset, list[str]] = UNSET
    redirect_uris: Union[Unset, list[str]] = UNSET
    web_origins: Union[Unset, list[str]] = UNSET
    not_before: Union[Unset, int] = UNSET
    bearer_only: Union[Unset, bool] = UNSET
    consent_required: Union[Unset, bool] = UNSET
    standard_flow_enabled: Union[Unset, bool] = UNSET
    implicit_flow_enabled: Union[Unset, bool] = UNSET
    direct_access_grants_enabled: Union[Unset, bool] = UNSET
    service_accounts_enabled: Union[Unset, bool] = UNSET
    authorization_services_enabled: Union[Unset, bool] = UNSET
    direct_grants_only: Union[Unset, bool] = UNSET
    public_client: Union[Unset, bool] = UNSET
    frontchannel_logout: Union[Unset, bool] = UNSET
    protocol: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'ClientRepresentationAttributes'] = UNSET
    authentication_flow_binding_overrides: Union[Unset, 'ClientRepresentationAuthenticationFlowBindingOverrides'] = UNSET
    full_scope_allowed: Union[Unset, bool] = UNSET
    node_re_registration_timeout: Union[Unset, int] = UNSET
    registered_nodes: Union[Unset, 'ClientRepresentationRegisteredNodes'] = UNSET
    protocol_mappers: Union[Unset, list['ProtocolMapperRepresentation']] = UNSET
    client_template: Union[Unset, str] = UNSET
    use_template_config: Union[Unset, bool] = UNSET
    use_template_scope: Union[Unset, bool] = UNSET
    use_template_mappers: Union[Unset, bool] = UNSET
    default_client_scopes: Union[Unset, list[str]] = UNSET
    optional_client_scopes: Union[Unset, list[str]] = UNSET
    authorization_settings: Union[Unset, 'ResourceServerRepresentation'] = UNSET
    access: Union[Unset, 'ClientRepresentationAccess'] = UNSET
    origin: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_representation_registered_nodes import ClientRepresentationRegisteredNodes
        from ..models.resource_server_representation import ResourceServerRepresentation
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        from ..models.client_representation_authentication_flow_binding_overrides import ClientRepresentationAuthenticationFlowBindingOverrides
        from ..models.client_representation_attributes import ClientRepresentationAttributes
        from ..models.client_representation_access import ClientRepresentationAccess
        id = self.id

        client_id = self.client_id

        name = self.name

        description = self.description

        type_ = self.type_

        root_url = self.root_url

        admin_url = self.admin_url

        base_url = self.base_url

        surrogate_auth_required = self.surrogate_auth_required

        enabled = self.enabled

        always_display_in_console = self.always_display_in_console

        client_authenticator_type = self.client_authenticator_type

        secret = self.secret

        registration_access_token = self.registration_access_token

        default_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.default_roles, Unset):
            default_roles = self.default_roles



        redirect_uris: Union[Unset, list[str]] = UNSET
        if not isinstance(self.redirect_uris, Unset):
            redirect_uris = self.redirect_uris



        web_origins: Union[Unset, list[str]] = UNSET
        if not isinstance(self.web_origins, Unset):
            web_origins = self.web_origins



        not_before = self.not_before

        bearer_only = self.bearer_only

        consent_required = self.consent_required

        standard_flow_enabled = self.standard_flow_enabled

        implicit_flow_enabled = self.implicit_flow_enabled

        direct_access_grants_enabled = self.direct_access_grants_enabled

        service_accounts_enabled = self.service_accounts_enabled

        authorization_services_enabled = self.authorization_services_enabled

        direct_grants_only = self.direct_grants_only

        public_client = self.public_client

        frontchannel_logout = self.frontchannel_logout

        protocol = self.protocol

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        authentication_flow_binding_overrides: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authentication_flow_binding_overrides, Unset):
            authentication_flow_binding_overrides = self.authentication_flow_binding_overrides.to_dict()

        full_scope_allowed = self.full_scope_allowed

        node_re_registration_timeout = self.node_re_registration_timeout

        registered_nodes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.registered_nodes, Unset):
            registered_nodes = self.registered_nodes.to_dict()

        protocol_mappers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.protocol_mappers, Unset):
            protocol_mappers = []
            for protocol_mappers_item_data in self.protocol_mappers:
                protocol_mappers_item = protocol_mappers_item_data.to_dict()
                protocol_mappers.append(protocol_mappers_item)



        client_template = self.client_template

        use_template_config = self.use_template_config

        use_template_scope = self.use_template_scope

        use_template_mappers = self.use_template_mappers

        default_client_scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.default_client_scopes, Unset):
            default_client_scopes = self.default_client_scopes



        optional_client_scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.optional_client_scopes, Unset):
            optional_client_scopes = self.optional_client_scopes



        authorization_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authorization_settings, Unset):
            authorization_settings = self.authorization_settings.to_dict()

        access: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.to_dict()

        origin = self.origin


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if type_ is not UNSET:
            field_dict["type"] = type_
        if root_url is not UNSET:
            field_dict["rootUrl"] = root_url
        if admin_url is not UNSET:
            field_dict["adminUrl"] = admin_url
        if base_url is not UNSET:
            field_dict["baseUrl"] = base_url
        if surrogate_auth_required is not UNSET:
            field_dict["surrogateAuthRequired"] = surrogate_auth_required
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if always_display_in_console is not UNSET:
            field_dict["alwaysDisplayInConsole"] = always_display_in_console
        if client_authenticator_type is not UNSET:
            field_dict["clientAuthenticatorType"] = client_authenticator_type
        if secret is not UNSET:
            field_dict["secret"] = secret
        if registration_access_token is not UNSET:
            field_dict["registrationAccessToken"] = registration_access_token
        if default_roles is not UNSET:
            field_dict["defaultRoles"] = default_roles
        if redirect_uris is not UNSET:
            field_dict["redirectUris"] = redirect_uris
        if web_origins is not UNSET:
            field_dict["webOrigins"] = web_origins
        if not_before is not UNSET:
            field_dict["notBefore"] = not_before
        if bearer_only is not UNSET:
            field_dict["bearerOnly"] = bearer_only
        if consent_required is not UNSET:
            field_dict["consentRequired"] = consent_required
        if standard_flow_enabled is not UNSET:
            field_dict["standardFlowEnabled"] = standard_flow_enabled
        if implicit_flow_enabled is not UNSET:
            field_dict["implicitFlowEnabled"] = implicit_flow_enabled
        if direct_access_grants_enabled is not UNSET:
            field_dict["directAccessGrantsEnabled"] = direct_access_grants_enabled
        if service_accounts_enabled is not UNSET:
            field_dict["serviceAccountsEnabled"] = service_accounts_enabled
        if authorization_services_enabled is not UNSET:
            field_dict["authorizationServicesEnabled"] = authorization_services_enabled
        if direct_grants_only is not UNSET:
            field_dict["directGrantsOnly"] = direct_grants_only
        if public_client is not UNSET:
            field_dict["publicClient"] = public_client
        if frontchannel_logout is not UNSET:
            field_dict["frontchannelLogout"] = frontchannel_logout
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if authentication_flow_binding_overrides is not UNSET:
            field_dict["authenticationFlowBindingOverrides"] = authentication_flow_binding_overrides
        if full_scope_allowed is not UNSET:
            field_dict["fullScopeAllowed"] = full_scope_allowed
        if node_re_registration_timeout is not UNSET:
            field_dict["nodeReRegistrationTimeout"] = node_re_registration_timeout
        if registered_nodes is not UNSET:
            field_dict["registeredNodes"] = registered_nodes
        if protocol_mappers is not UNSET:
            field_dict["protocolMappers"] = protocol_mappers
        if client_template is not UNSET:
            field_dict["clientTemplate"] = client_template
        if use_template_config is not UNSET:
            field_dict["useTemplateConfig"] = use_template_config
        if use_template_scope is not UNSET:
            field_dict["useTemplateScope"] = use_template_scope
        if use_template_mappers is not UNSET:
            field_dict["useTemplateMappers"] = use_template_mappers
        if default_client_scopes is not UNSET:
            field_dict["defaultClientScopes"] = default_client_scopes
        if optional_client_scopes is not UNSET:
            field_dict["optionalClientScopes"] = optional_client_scopes
        if authorization_settings is not UNSET:
            field_dict["authorizationSettings"] = authorization_settings
        if access is not UNSET:
            field_dict["access"] = access
        if origin is not UNSET:
            field_dict["origin"] = origin

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_representation_registered_nodes import ClientRepresentationRegisteredNodes
        from ..models.resource_server_representation import ResourceServerRepresentation
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        from ..models.client_representation_authentication_flow_binding_overrides import ClientRepresentationAuthenticationFlowBindingOverrides
        from ..models.client_representation_attributes import ClientRepresentationAttributes
        from ..models.client_representation_access import ClientRepresentationAccess
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        client_id = d.pop("clientId", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        type_ = d.pop("type", UNSET)

        root_url = d.pop("rootUrl", UNSET)

        admin_url = d.pop("adminUrl", UNSET)

        base_url = d.pop("baseUrl", UNSET)

        surrogate_auth_required = d.pop("surrogateAuthRequired", UNSET)

        enabled = d.pop("enabled", UNSET)

        always_display_in_console = d.pop("alwaysDisplayInConsole", UNSET)

        client_authenticator_type = d.pop("clientAuthenticatorType", UNSET)

        secret = d.pop("secret", UNSET)

        registration_access_token = d.pop("registrationAccessToken", UNSET)

        default_roles = cast(list[str], d.pop("defaultRoles", UNSET))


        redirect_uris = cast(list[str], d.pop("redirectUris", UNSET))


        web_origins = cast(list[str], d.pop("webOrigins", UNSET))


        not_before = d.pop("notBefore", UNSET)

        bearer_only = d.pop("bearerOnly", UNSET)

        consent_required = d.pop("consentRequired", UNSET)

        standard_flow_enabled = d.pop("standardFlowEnabled", UNSET)

        implicit_flow_enabled = d.pop("implicitFlowEnabled", UNSET)

        direct_access_grants_enabled = d.pop("directAccessGrantsEnabled", UNSET)

        service_accounts_enabled = d.pop("serviceAccountsEnabled", UNSET)

        authorization_services_enabled = d.pop("authorizationServicesEnabled", UNSET)

        direct_grants_only = d.pop("directGrantsOnly", UNSET)

        public_client = d.pop("publicClient", UNSET)

        frontchannel_logout = d.pop("frontchannelLogout", UNSET)

        protocol = d.pop("protocol", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, ClientRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = ClientRepresentationAttributes.from_dict(_attributes)




        _authentication_flow_binding_overrides = d.pop("authenticationFlowBindingOverrides", UNSET)
        authentication_flow_binding_overrides: Union[Unset, ClientRepresentationAuthenticationFlowBindingOverrides]
        if isinstance(_authentication_flow_binding_overrides,  Unset):
            authentication_flow_binding_overrides = UNSET
        else:
            authentication_flow_binding_overrides = ClientRepresentationAuthenticationFlowBindingOverrides.from_dict(_authentication_flow_binding_overrides)




        full_scope_allowed = d.pop("fullScopeAllowed", UNSET)

        node_re_registration_timeout = d.pop("nodeReRegistrationTimeout", UNSET)

        _registered_nodes = d.pop("registeredNodes", UNSET)
        registered_nodes: Union[Unset, ClientRepresentationRegisteredNodes]
        if isinstance(_registered_nodes,  Unset):
            registered_nodes = UNSET
        else:
            registered_nodes = ClientRepresentationRegisteredNodes.from_dict(_registered_nodes)




        protocol_mappers = []
        _protocol_mappers = d.pop("protocolMappers", UNSET)
        for protocol_mappers_item_data in (_protocol_mappers or []):
            protocol_mappers_item = ProtocolMapperRepresentation.from_dict(protocol_mappers_item_data)



            protocol_mappers.append(protocol_mappers_item)


        client_template = d.pop("clientTemplate", UNSET)

        use_template_config = d.pop("useTemplateConfig", UNSET)

        use_template_scope = d.pop("useTemplateScope", UNSET)

        use_template_mappers = d.pop("useTemplateMappers", UNSET)

        default_client_scopes = cast(list[str], d.pop("defaultClientScopes", UNSET))


        optional_client_scopes = cast(list[str], d.pop("optionalClientScopes", UNSET))


        _authorization_settings = d.pop("authorizationSettings", UNSET)
        authorization_settings: Union[Unset, ResourceServerRepresentation]
        if isinstance(_authorization_settings,  Unset):
            authorization_settings = UNSET
        else:
            authorization_settings = ResourceServerRepresentation.from_dict(_authorization_settings)




        _access = d.pop("access", UNSET)
        access: Union[Unset, ClientRepresentationAccess]
        if isinstance(_access,  Unset):
            access = UNSET
        else:
            access = ClientRepresentationAccess.from_dict(_access)




        origin = d.pop("origin", UNSET)

        client_representation = cls(
            id=id,
            client_id=client_id,
            name=name,
            description=description,
            type_=type_,
            root_url=root_url,
            admin_url=admin_url,
            base_url=base_url,
            surrogate_auth_required=surrogate_auth_required,
            enabled=enabled,
            always_display_in_console=always_display_in_console,
            client_authenticator_type=client_authenticator_type,
            secret=secret,
            registration_access_token=registration_access_token,
            default_roles=default_roles,
            redirect_uris=redirect_uris,
            web_origins=web_origins,
            not_before=not_before,
            bearer_only=bearer_only,
            consent_required=consent_required,
            standard_flow_enabled=standard_flow_enabled,
            implicit_flow_enabled=implicit_flow_enabled,
            direct_access_grants_enabled=direct_access_grants_enabled,
            service_accounts_enabled=service_accounts_enabled,
            authorization_services_enabled=authorization_services_enabled,
            direct_grants_only=direct_grants_only,
            public_client=public_client,
            frontchannel_logout=frontchannel_logout,
            protocol=protocol,
            attributes=attributes,
            authentication_flow_binding_overrides=authentication_flow_binding_overrides,
            full_scope_allowed=full_scope_allowed,
            node_re_registration_timeout=node_re_registration_timeout,
            registered_nodes=registered_nodes,
            protocol_mappers=protocol_mappers,
            client_template=client_template,
            use_template_config=use_template_config,
            use_template_scope=use_template_scope,
            use_template_mappers=use_template_mappers,
            default_client_scopes=default_client_scopes,
            optional_client_scopes=optional_client_scopes,
            authorization_settings=authorization_settings,
            access=access,
            origin=origin,
        )


        client_representation.additional_properties = d
        return client_representation

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
