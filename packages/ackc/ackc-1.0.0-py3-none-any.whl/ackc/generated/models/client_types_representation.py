from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_type_representation import ClientTypeRepresentation





T = TypeVar("T", bound="ClientTypesRepresentation")



@_attrs_define
class ClientTypesRepresentation:
    """ 
        Attributes:
            client_types (Union[Unset, list['ClientTypeRepresentation']]):
            global_client_types (Union[Unset, list['ClientTypeRepresentation']]):
     """

    client_types: Union[Unset, list['ClientTypeRepresentation']] = UNSET
    global_client_types: Union[Unset, list['ClientTypeRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_type_representation import ClientTypeRepresentation
        client_types: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.client_types, Unset):
            client_types = []
            for client_types_item_data in self.client_types:
                client_types_item = client_types_item_data.to_dict()
                client_types.append(client_types_item)



        global_client_types: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.global_client_types, Unset):
            global_client_types = []
            for global_client_types_item_data in self.global_client_types:
                global_client_types_item = global_client_types_item_data.to_dict()
                global_client_types.append(global_client_types_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if client_types is not UNSET:
            field_dict["client-types"] = client_types
        if global_client_types is not UNSET:
            field_dict["global-client-types"] = global_client_types

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_type_representation import ClientTypeRepresentation
        d = dict(src_dict)
        client_types = []
        _client_types = d.pop("client-types", UNSET)
        for client_types_item_data in (_client_types or []):
            client_types_item = ClientTypeRepresentation.from_dict(client_types_item_data)



            client_types.append(client_types_item)


        global_client_types = []
        _global_client_types = d.pop("global-client-types", UNSET)
        for global_client_types_item_data in (_global_client_types or []):
            global_client_types_item = ClientTypeRepresentation.from_dict(global_client_types_item_data)



            global_client_types.append(global_client_types_item)


        client_types_representation = cls(
            client_types=client_types,
            global_client_types=global_client_types,
        )


        client_types_representation.additional_properties = d
        return client_types_representation

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
