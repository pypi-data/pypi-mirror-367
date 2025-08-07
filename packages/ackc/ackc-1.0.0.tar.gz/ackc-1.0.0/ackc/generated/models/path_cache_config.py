from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PathCacheConfig")



@_attrs_define
class PathCacheConfig:
    """ 
        Attributes:
            max_entries (Union[Unset, int]):
            lifespan (Union[Unset, int]):
     """

    max_entries: Union[Unset, int] = UNSET
    lifespan: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        max_entries = self.max_entries

        lifespan = self.lifespan


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if max_entries is not UNSET:
            field_dict["max-entries"] = max_entries
        if lifespan is not UNSET:
            field_dict["lifespan"] = lifespan

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_entries = d.pop("max-entries", UNSET)

        lifespan = d.pop("lifespan", UNSET)

        path_cache_config = cls(
            max_entries=max_entries,
            lifespan=lifespan,
        )


        path_cache_config.additional_properties = d
        return path_cache_config

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
