from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.config_property_representation import ConfigPropertyRepresentation





T = TypeVar("T", bound="RequiredActionConfigInfoRepresentation")



@_attrs_define
class RequiredActionConfigInfoRepresentation:
    """ 
        Attributes:
            properties (Union[Unset, list['ConfigPropertyRepresentation']]):
     """

    properties: Union[Unset, list['ConfigPropertyRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.config_property_representation import ConfigPropertyRepresentation
        properties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.config_property_representation import ConfigPropertyRepresentation
        d = dict(src_dict)
        properties = []
        _properties = d.pop("properties", UNSET)
        for properties_item_data in (_properties or []):
            properties_item = ConfigPropertyRepresentation.from_dict(properties_item_data)



            properties.append(properties_item)


        required_action_config_info_representation = cls(
            properties=properties,
        )


        required_action_config_info_representation.additional_properties = d
        return required_action_config_info_representation

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
