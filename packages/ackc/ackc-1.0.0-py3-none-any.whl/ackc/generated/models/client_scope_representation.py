from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
  from ..models.client_scope_representation_attributes import ClientScopeRepresentationAttributes





T = TypeVar("T", bound="ClientScopeRepresentation")



@_attrs_define
class ClientScopeRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            protocol (Union[Unset, str]):
            attributes (Union[Unset, ClientScopeRepresentationAttributes]):
            protocol_mappers (Union[Unset, list['ProtocolMapperRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    protocol: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'ClientScopeRepresentationAttributes'] = UNSET
    protocol_mappers: Union[Unset, list['ProtocolMapperRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        from ..models.client_scope_representation_attributes import ClientScopeRepresentationAttributes
        id = self.id

        name = self.name

        description = self.description

        protocol = self.protocol

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
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if protocol_mappers is not UNSET:
            field_dict["protocolMappers"] = protocol_mappers

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.protocol_mapper_representation import ProtocolMapperRepresentation
        from ..models.client_scope_representation_attributes import ClientScopeRepresentationAttributes
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        protocol = d.pop("protocol", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, ClientScopeRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = ClientScopeRepresentationAttributes.from_dict(_attributes)




        protocol_mappers = []
        _protocol_mappers = d.pop("protocolMappers", UNSET)
        for protocol_mappers_item_data in (_protocol_mappers or []):
            protocol_mappers_item = ProtocolMapperRepresentation.from_dict(protocol_mappers_item_data)



            protocol_mappers.append(protocol_mappers_item)


        client_scope_representation = cls(
            id=id,
            name=name,
            description=description,
            protocol=protocol,
            attributes=attributes,
            protocol_mappers=protocol_mappers,
        )


        client_scope_representation.additional_properties = d
        return client_scope_representation

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
