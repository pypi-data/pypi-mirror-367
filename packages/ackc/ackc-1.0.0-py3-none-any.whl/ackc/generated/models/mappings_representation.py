from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.role_representation import RoleRepresentation
  from ..models.mappings_representation_client_mappings import MappingsRepresentationClientMappings





T = TypeVar("T", bound="MappingsRepresentation")



@_attrs_define
class MappingsRepresentation:
    """ 
        Attributes:
            realm_mappings (Union[Unset, list['RoleRepresentation']]):
            client_mappings (Union[Unset, MappingsRepresentationClientMappings]):
     """

    realm_mappings: Union[Unset, list['RoleRepresentation']] = UNSET
    client_mappings: Union[Unset, 'MappingsRepresentationClientMappings'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.role_representation import RoleRepresentation
        from ..models.mappings_representation_client_mappings import MappingsRepresentationClientMappings
        realm_mappings: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.realm_mappings, Unset):
            realm_mappings = []
            for realm_mappings_item_data in self.realm_mappings:
                realm_mappings_item = realm_mappings_item_data.to_dict()
                realm_mappings.append(realm_mappings_item)



        client_mappings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client_mappings, Unset):
            client_mappings = self.client_mappings.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if realm_mappings is not UNSET:
            field_dict["realmMappings"] = realm_mappings
        if client_mappings is not UNSET:
            field_dict["clientMappings"] = client_mappings

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.role_representation import RoleRepresentation
        from ..models.mappings_representation_client_mappings import MappingsRepresentationClientMappings
        d = dict(src_dict)
        realm_mappings = []
        _realm_mappings = d.pop("realmMappings", UNSET)
        for realm_mappings_item_data in (_realm_mappings or []):
            realm_mappings_item = RoleRepresentation.from_dict(realm_mappings_item_data)



            realm_mappings.append(realm_mappings_item)


        _client_mappings = d.pop("clientMappings", UNSET)
        client_mappings: Union[Unset, MappingsRepresentationClientMappings]
        if isinstance(_client_mappings,  Unset):
            client_mappings = UNSET
        else:
            client_mappings = MappingsRepresentationClientMappings.from_dict(_client_mappings)




        mappings_representation = cls(
            realm_mappings=realm_mappings,
            client_mappings=client_mappings,
        )


        mappings_representation.additional_properties = d
        return mappings_representation

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
