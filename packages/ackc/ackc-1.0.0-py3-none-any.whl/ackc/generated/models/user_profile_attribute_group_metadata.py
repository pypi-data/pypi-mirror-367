from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_profile_attribute_group_metadata_annotations import UserProfileAttributeGroupMetadataAnnotations





T = TypeVar("T", bound="UserProfileAttributeGroupMetadata")



@_attrs_define
class UserProfileAttributeGroupMetadata:
    """ 
        Attributes:
            name (Union[Unset, str]):
            display_header (Union[Unset, str]):
            display_description (Union[Unset, str]):
            annotations (Union[Unset, UserProfileAttributeGroupMetadataAnnotations]):
     """

    name: Union[Unset, str] = UNSET
    display_header: Union[Unset, str] = UNSET
    display_description: Union[Unset, str] = UNSET
    annotations: Union[Unset, 'UserProfileAttributeGroupMetadataAnnotations'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_profile_attribute_group_metadata_annotations import UserProfileAttributeGroupMetadataAnnotations
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
        from ..models.user_profile_attribute_group_metadata_annotations import UserProfileAttributeGroupMetadataAnnotations
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        display_header = d.pop("displayHeader", UNSET)

        display_description = d.pop("displayDescription", UNSET)

        _annotations = d.pop("annotations", UNSET)
        annotations: Union[Unset, UserProfileAttributeGroupMetadataAnnotations]
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = UserProfileAttributeGroupMetadataAnnotations.from_dict(_annotations)




        user_profile_attribute_group_metadata = cls(
            name=name,
            display_header=display_header,
            display_description=display_description,
            annotations=annotations,
        )


        user_profile_attribute_group_metadata.additional_properties = d
        return user_profile_attribute_group_metadata

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
