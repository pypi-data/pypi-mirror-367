from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_template_representation_attributes import ClientTemplateRepresentationAttributes
  from ..models.protocol_mapper_representation import ProtocolMapperRepresentation





T = TypeVar("T", bound="ClientTemplateRepresentation")



@_attrs_define
class ClientTemplateRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            protocol (Union[Unset, str]):
            full_scope_allowed (Union[Unset, bool]):
            bearer_only (Union[Unset, bool]):
            consent_required (Union[Unset, bool]):
            standard_flow_enabled (Union[Unset, bool]):
            implicit_flow_enabled (Union[Unset, bool]):
            direct_access_grants_enabled (Union[Unset, bool]):
            service_accounts_enabled (Union[Unset, bool]):
            public_client (Union[Unset, bool]):
            frontchannel_logout (Union[Unset, bool]):
            attributes (Union[Unset, ClientTemplateRepresentationAttributes]):
            protocol_mappers (Union[Unset, list['ProtocolMapperRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    protocol: Union[Unset, str] = UNSET
    full_scope_allowed: Union[Unset, bool] = UNSET
    bearer_only: Union[Unset, bool] = UNSET
    consent_required: Union[Unset, bool] = UNSET
    standard_flow_enabled: Union[Unset, bool] = UNSET
    implicit_flow_enabled: Union[Unset, bool] = UNSET
    direct_access_grants_enabled: Union[Unset, bool] = UNSET
    service_accounts_enabled: Union[Unset, bool] = UNSET
    public_client: Union[Unset, bool] = UNSET
    frontchannel_logout: Union[Unset, bool] = UNSET
    attributes: Union[Unset, 'ClientTemplateRepresentationAttributes'] = UNSET
    protocol_mappers: Union[Unset, list['ProtocolMapperRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_template_representation_attributes import ClientTemplateRepresentationAttributes
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        id = self.id

        name = self.name

        description = self.description

        protocol = self.protocol

        full_scope_allowed = self.full_scope_allowed

        bearer_only = self.bearer_only

        consent_required = self.consent_required

        standard_flow_enabled = self.standard_flow_enabled

        implicit_flow_enabled = self.implicit_flow_enabled

        direct_access_grants_enabled = self.direct_access_grants_enabled

        service_accounts_enabled = self.service_accounts_enabled

        public_client = self.public_client

        frontchannel_logout = self.frontchannel_logout

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        protocol_mappers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.protocol_mappers, Unset):
            protocol_mappers = []
            for protocol_mappers_item_data in self.protocol_mappers:
                protocol_mappers_item = protocol_mappers_item_data.to_dict()
                protocol_mappers.append(protocol_mappers_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if full_scope_allowed is not UNSET:
            field_dict["fullScopeAllowed"] = full_scope_allowed
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
        if public_client is not UNSET:
            field_dict["publicClient"] = public_client
        if frontchannel_logout is not UNSET:
            field_dict["frontchannelLogout"] = frontchannel_logout
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if protocol_mappers is not UNSET:
            field_dict["protocolMappers"] = protocol_mappers

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_template_representation_attributes import ClientTemplateRepresentationAttributes
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        protocol = d.pop("protocol", UNSET)

        full_scope_allowed = d.pop("fullScopeAllowed", UNSET)

        bearer_only = d.pop("bearerOnly", UNSET)

        consent_required = d.pop("consentRequired", UNSET)

        standard_flow_enabled = d.pop("standardFlowEnabled", UNSET)

        implicit_flow_enabled = d.pop("implicitFlowEnabled", UNSET)

        direct_access_grants_enabled = d.pop("directAccessGrantsEnabled", UNSET)

        service_accounts_enabled = d.pop("serviceAccountsEnabled", UNSET)

        public_client = d.pop("publicClient", UNSET)

        frontchannel_logout = d.pop("frontchannelLogout", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, ClientTemplateRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = ClientTemplateRepresentationAttributes.from_dict(_attributes)




        protocol_mappers = []
        _protocol_mappers = d.pop("protocolMappers", UNSET)
        for protocol_mappers_item_data in (_protocol_mappers or []):
            protocol_mappers_item = ProtocolMapperRepresentation.from_dict(protocol_mappers_item_data)



            protocol_mappers.append(protocol_mappers_item)


        client_template_representation = cls(
            id=id,
            name=name,
            description=description,
            protocol=protocol,
            full_scope_allowed=full_scope_allowed,
            bearer_only=bearer_only,
            consent_required=consent_required,
            standard_flow_enabled=standard_flow_enabled,
            implicit_flow_enabled=implicit_flow_enabled,
            direct_access_grants_enabled=direct_access_grants_enabled,
            service_accounts_enabled=service_accounts_enabled,
            public_client=public_client,
            frontchannel_logout=frontchannel_logout,
            attributes=attributes,
            protocol_mappers=protocol_mappers,
        )


        client_template_representation.additional_properties = d
        return client_template_representation

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
