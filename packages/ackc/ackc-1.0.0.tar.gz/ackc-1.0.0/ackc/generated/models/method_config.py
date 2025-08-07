from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.scope_enforcement_mode import ScopeEnforcementMode
from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="MethodConfig")



@_attrs_define
class MethodConfig:
    """ 
        Attributes:
            method (Union[Unset, str]):
            scopes (Union[Unset, list[str]]):
            scopes_enforcement_mode (Union[Unset, ScopeEnforcementMode]):
     """

    method: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    scopes_enforcement_mode: Union[Unset, ScopeEnforcementMode] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        method = self.method

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        scopes_enforcement_mode: Union[Unset, str] = UNSET
        if not isinstance(self.scopes_enforcement_mode, Unset):
            scopes_enforcement_mode = self.scopes_enforcement_mode.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if method is not UNSET:
            field_dict["method"] = method
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if scopes_enforcement_mode is not UNSET:
            field_dict["scopes-enforcement-mode"] = scopes_enforcement_mode

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        method = d.pop("method", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _scopes_enforcement_mode = d.pop("scopes-enforcement-mode", UNSET)
        scopes_enforcement_mode: Union[Unset, ScopeEnforcementMode]
        if isinstance(_scopes_enforcement_mode,  Unset):
            scopes_enforcement_mode = UNSET
        else:
            scopes_enforcement_mode = ScopeEnforcementMode(_scopes_enforcement_mode)




        method_config = cls(
            method=method,
            scopes=scopes,
            scopes_enforcement_mode=scopes_enforcement_mode,
        )


        method_config.additional_properties = d
        return method_config

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
