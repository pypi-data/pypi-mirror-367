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





T = TypeVar("T", bound="IdentityProviderMapperTypeRepresentation")



@_attrs_define
class IdentityProviderMapperTypeRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            category (Union[Unset, str]):
            help_text (Union[Unset, str]):
            properties (Union[Unset, list['ConfigPropertyRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    category: Union[Unset, str] = UNSET
    help_text: Union[Unset, str] = UNSET
    properties: Union[Unset, list['ConfigPropertyRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.config_property_representation import ConfigPropertyRepresentation
        id = self.id

        name = self.name

        category = self.category

        help_text = self.help_text

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
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if category is not UNSET:
            field_dict["category"] = category
        if help_text is not UNSET:
            field_dict["helpText"] = help_text
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.config_property_representation import ConfigPropertyRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        category = d.pop("category", UNSET)

        help_text = d.pop("helpText", UNSET)

        properties = []
        _properties = d.pop("properties", UNSET)
        for properties_item_data in (_properties or []):
            properties_item = ConfigPropertyRepresentation.from_dict(properties_item_data)



            properties.append(properties_item)


        identity_provider_mapper_type_representation = cls(
            id=id,
            name=name,
            category=category,
            help_text=help_text,
            properties=properties,
        )


        identity_provider_mapper_type_representation.additional_properties = d
        return identity_provider_mapper_type_representation

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
