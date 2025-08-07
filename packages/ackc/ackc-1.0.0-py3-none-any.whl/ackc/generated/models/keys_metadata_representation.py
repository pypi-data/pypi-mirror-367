from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.keys_metadata_representation_active import KeysMetadataRepresentationActive
  from ..models.key_metadata_representation import KeyMetadataRepresentation





T = TypeVar("T", bound="KeysMetadataRepresentation")



@_attrs_define
class KeysMetadataRepresentation:
    """ 
        Attributes:
            active (Union[Unset, KeysMetadataRepresentationActive]):
            keys (Union[Unset, list['KeyMetadataRepresentation']]):
     """

    active: Union[Unset, 'KeysMetadataRepresentationActive'] = UNSET
    keys: Union[Unset, list['KeyMetadataRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.keys_metadata_representation_active import KeysMetadataRepresentationActive
        from ..models.key_metadata_representation import KeyMetadataRepresentation
        active: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.active, Unset):
            active = self.active.to_dict()

        keys: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.keys, Unset):
            keys = []
            for keys_item_data in self.keys:
                keys_item = keys_item_data.to_dict()
                keys.append(keys_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if active is not UNSET:
            field_dict["active"] = active
        if keys is not UNSET:
            field_dict["keys"] = keys

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.keys_metadata_representation_active import KeysMetadataRepresentationActive
        from ..models.key_metadata_representation import KeyMetadataRepresentation
        d = dict(src_dict)
        _active = d.pop("active", UNSET)
        active: Union[Unset, KeysMetadataRepresentationActive]
        if isinstance(_active,  Unset):
            active = UNSET
        else:
            active = KeysMetadataRepresentationActive.from_dict(_active)




        keys = []
        _keys = d.pop("keys", UNSET)
        for keys_item_data in (_keys or []):
            keys_item = KeyMetadataRepresentation.from_dict(keys_item_data)



            keys.append(keys_item)


        keys_metadata_representation = cls(
            active=active,
            keys=keys,
        )


        keys_metadata_representation.additional_properties = d
        return keys_metadata_representation

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
