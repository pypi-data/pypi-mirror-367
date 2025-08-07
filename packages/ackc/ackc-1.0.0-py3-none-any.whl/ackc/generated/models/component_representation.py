from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString





T = TypeVar("T", bound="ComponentRepresentation")



@_attrs_define
class ComponentRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            provider_id (Union[Unset, str]):
            provider_type (Union[Unset, str]):
            parent_id (Union[Unset, str]):
            sub_type (Union[Unset, str]):
            config (Union[Unset, MultivaluedHashMapStringString]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    provider_id: Union[Unset, str] = UNSET
    provider_type: Union[Unset, str] = UNSET
    parent_id: Union[Unset, str] = UNSET
    sub_type: Union[Unset, str] = UNSET
    config: Union[Unset, 'MultivaluedHashMapStringString'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString
        id = self.id

        name = self.name

        provider_id = self.provider_id

        provider_type = self.provider_type

        parent_id = self.parent_id

        sub_type = self.sub_type

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
        if provider_type is not UNSET:
            field_dict["providerType"] = provider_type
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if sub_type is not UNSET:
            field_dict["subType"] = sub_type
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        provider_id = d.pop("providerId", UNSET)

        provider_type = d.pop("providerType", UNSET)

        parent_id = d.pop("parentId", UNSET)

        sub_type = d.pop("subType", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, MultivaluedHashMapStringString]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = MultivaluedHashMapStringString.from_dict(_config)




        component_representation = cls(
            id=id,
            name=name,
            provider_id=provider_id,
            provider_type=provider_type,
            parent_id=parent_id,
            sub_type=sub_type,
            config=config,
        )


        component_representation.additional_properties = d
        return component_representation

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
