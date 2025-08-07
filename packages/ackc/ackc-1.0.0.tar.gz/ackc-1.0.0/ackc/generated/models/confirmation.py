from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="Confirmation")



@_attrs_define
class Confirmation:
    """ 
        Attributes:
            x_5_t_s256 (Union[Unset, str]):
            jkt (Union[Unset, str]):
     """

    x_5_t_s256: Union[Unset, str] = UNSET
    jkt: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        x_5_t_s256 = self.x_5_t_s256

        jkt = self.jkt


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if x_5_t_s256 is not UNSET:
            field_dict["x5t#S256"] = x_5_t_s256
        if jkt is not UNSET:
            field_dict["jkt"] = jkt

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        x_5_t_s256 = d.pop("x5t#S256", UNSET)

        jkt = d.pop("jkt", UNSET)

        confirmation = cls(
            x_5_t_s256=x_5_t_s256,
            jkt=jkt,
        )


        confirmation.additional_properties = d
        return confirmation

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
