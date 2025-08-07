from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.up_group_annotations import UPGroupAnnotations





T = TypeVar("T", bound="UPGroup")



@_attrs_define
class UPGroup:
    """ 
        Attributes:
            name (Union[Unset, str]):
            display_header (Union[Unset, str]):
            display_description (Union[Unset, str]):
            annotations (Union[Unset, UPGroupAnnotations]):
     """

    name: Union[Unset, str] = UNSET
    display_header: Union[Unset, str] = UNSET
    display_description: Union[Unset, str] = UNSET
    annotations: Union[Unset, 'UPGroupAnnotations'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.up_group_annotations import UPGroupAnnotations
        name = self.name

        display_header = self.display_header

        display_description = self.display_description

        annotations: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = self.annotations.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if display_header is not UNSET:
            field_dict["displayHeader"] = display_header
        if display_description is not UNSET:
            field_dict["displayDescription"] = display_description
        if annotations is not UNSET:
            field_dict["annotations"] = annotations

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.up_group_annotations import UPGroupAnnotations
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        display_header = d.pop("displayHeader", UNSET)

        display_description = d.pop("displayDescription", UNSET)

        _annotations = d.pop("annotations", UNSET)
        annotations: Union[Unset, UPGroupAnnotations]
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = UPGroupAnnotations.from_dict(_annotations)




        up_group = cls(
            name=name,
            display_header=display_header,
            display_description=display_description,
            annotations=annotations,
        )


        up_group.additional_properties = d
        return up_group

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
