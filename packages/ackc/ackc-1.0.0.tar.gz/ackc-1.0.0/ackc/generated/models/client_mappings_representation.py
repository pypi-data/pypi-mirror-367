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





T = TypeVar("T", bound="ClientMappingsRepresentation")



@_attrs_define
class ClientMappingsRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            client (Union[Unset, str]):
            mappings (Union[Unset, list['RoleRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    client: Union[Unset, str] = UNSET
    mappings: Union[Unset, list['RoleRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.role_representation import RoleRepresentation
        id = self.id

        client = self.client

        mappings: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.mappings, Unset):
            mappings = []
            for mappings_item_data in self.mappings:
                mappings_item = mappings_item_data.to_dict()
                mappings.append(mappings_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if client is not UNSET:
            field_dict["client"] = client
        if mappings is not UNSET:
            field_dict["mappings"] = mappings

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.role_representation import RoleRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        client = d.pop("client", UNSET)

        mappings = []
        _mappings = d.pop("mappings", UNSET)
        for mappings_item_data in (_mappings or []):
            mappings_item = RoleRepresentation.from_dict(mappings_item_data)



            mappings.append(mappings_item)


        client_mappings_representation = cls(
            id=id,
            client=client,
            mappings=mappings,
        )


        client_mappings_representation.additional_properties = d
        return client_mappings_representation

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
