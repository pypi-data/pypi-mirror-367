from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.permission import Permission





T = TypeVar("T", bound="Authorization")



@_attrs_define
class Authorization:
    """ 
        Attributes:
            permissions (Union[Unset, list['Permission']]):
     """

    permissions: Union[Unset, list['Permission']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.permission import Permission
        permissions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = []
            for permissions_item_data in self.permissions:
                permissions_item = permissions_item_data.to_dict()
                permissions.append(permissions_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.permission import Permission
        d = dict(src_dict)
        permissions = []
        _permissions = d.pop("permissions", UNSET)
        for permissions_item_data in (_permissions or []):
            permissions_item = Permission.from_dict(permissions_item_data)



            permissions.append(permissions_item)


        authorization = cls(
            permissions=permissions,
        )


        authorization.additional_properties = d
        return authorization

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
