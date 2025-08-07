from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
  from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString





T = TypeVar("T", bound="ComponentExportRepresentation")



@_attrs_define
class ComponentExportRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            provider_id (Union[Unset, str]):
            sub_type (Union[Unset, str]):
            sub_components (Union[Unset, MultivaluedHashMapStringComponentExportRepresentation]):
            config (Union[Unset, MultivaluedHashMapStringString]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    provider_id: Union[Unset, str] = UNSET
    sub_type: Union[Unset, str] = UNSET
    sub_components: Union[Unset, 'MultivaluedHashMapStringComponentExportRepresentation'] = UNSET
    config: Union[Unset, 'MultivaluedHashMapStringString'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
        from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString
        id = self.id

        name = self.name

        provider_id = self.provider_id

        sub_type = self.sub_type

        sub_components: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sub_components, Unset):
            sub_components = self.sub_components.to_dict()

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if provider_id is not UNSET:
            field_dict["providerId"] = provider_id
        if sub_type is not UNSET:
            field_dict["subType"] = sub_type
        if sub_components is not UNSET:
            field_dict["subComponents"] = sub_components
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.multivalued_hash_map_string_component_export_representation import MultivaluedHashMapStringComponentExportRepresentation
        from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        provider_id = d.pop("providerId", UNSET)

        sub_type = d.pop("subType", UNSET)

        _sub_components = d.pop("subComponents", UNSET)
        sub_components: Union[Unset, MultivaluedHashMapStringComponentExportRepresentation]
        if isinstance(_sub_components,  Unset):
            sub_components = UNSET
        else:
            sub_components = MultivaluedHashMapStringComponentExportRepresentation.from_dict(_sub_components)




        _config = d.pop("config", UNSET)
        config: Union[Unset, MultivaluedHashMapStringString]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = MultivaluedHashMapStringString.from_dict(_config)




        component_export_representation = cls(
            id=id,
            name=name,
            provider_id=provider_id,
            sub_type=sub_type,
            sub_components=sub_components,
            config=config,
        )


        component_export_representation.additional_properties = d
        return component_export_representation

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
