from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.resource_type_scope_aliases import ResourceTypeScopeAliases





T = TypeVar("T", bound="ResourceType")



@_attrs_define
class ResourceType:
    """ 
        Attributes:
            type_ (Union[Unset, str]):
            scopes (Union[Unset, list[str]]):
            scope_aliases (Union[Unset, ResourceTypeScopeAliases]):
            group_type (Union[Unset, str]):
     """

    type_: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    scope_aliases: Union[Unset, 'ResourceTypeScopeAliases'] = UNSET
    group_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.resource_type_scope_aliases import ResourceTypeScopeAliases
        type_ = self.type_

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        scope_aliases: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.scope_aliases, Unset):
            scope_aliases = self.scope_aliases.to_dict()

        group_type = self.group_type


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if scope_aliases is not UNSET:
            field_dict["scopeAliases"] = scope_aliases
        if group_type is not UNSET:
            field_dict["groupType"] = group_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_type_scope_aliases import ResourceTypeScopeAliases
        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _scope_aliases = d.pop("scopeAliases", UNSET)
        scope_aliases: Union[Unset, ResourceTypeScopeAliases]
        if isinstance(_scope_aliases,  Unset):
            scope_aliases = UNSET
        else:
            scope_aliases = ResourceTypeScopeAliases.from_dict(_scope_aliases)




        group_type = d.pop("groupType", UNSET)

        resource_type = cls(
            type_=type_,
            scopes=scopes,
            scope_aliases=scope_aliases,
            group_type=group_type,
        )


        resource_type.additional_properties = d
        return resource_type

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
