from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="UPAttributePermissions")



@_attrs_define
class UPAttributePermissions:
    """ 
        Attributes:
            view (Union[Unset, list[str]]):
            edit (Union[Unset, list[str]]):
     """

    view: Union[Unset, list[str]] = UNSET
    edit: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        view: Union[Unset, list[str]] = UNSET
        if not isinstance(self.view, Unset):
            view = self.view



        edit: Union[Unset, list[str]] = UNSET
        if not isinstance(self.edit, Unset):
            edit = self.edit




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if view is not UNSET:
            field_dict["view"] = view
        if edit is not UNSET:
            field_dict["edit"] = edit

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        view = cast(list[str], d.pop("view", UNSET))


        edit = cast(list[str], d.pop("edit", UNSET))


        up_attribute_permissions = cls(
            view=view,
            edit=edit,
        )


        up_attribute_permissions.additional_properties = d
        return up_attribute_permissions

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
