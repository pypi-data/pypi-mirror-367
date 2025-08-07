from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_profile_attribute_group_metadata import UserProfileAttributeGroupMetadata
  from ..models.user_profile_attribute_metadata import UserProfileAttributeMetadata





T = TypeVar("T", bound="UserProfileMetadata")



@_attrs_define
class UserProfileMetadata:
    """ 
        Attributes:
            attributes (Union[Unset, list['UserProfileAttributeMetadata']]):
            groups (Union[Unset, list['UserProfileAttributeGroupMetadata']]):
     """

    attributes: Union[Unset, list['UserProfileAttributeMetadata']] = UNSET
    groups: Union[Unset, list['UserProfileAttributeGroupMetadata']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_profile_attribute_group_metadata import UserProfileAttributeGroupMetadata
        from ..models.user_profile_attribute_metadata import UserProfileAttributeMetadata
        attributes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = []
            for attributes_item_data in self.attributes:
                attributes_item = attributes_item_data.to_dict()
                attributes.append(attributes_item)



        groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if groups is not UNSET:
            field_dict["groups"] = groups

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_profile_attribute_group_metadata import UserProfileAttributeGroupMetadata
        from ..models.user_profile_attribute_metadata import UserProfileAttributeMetadata
        d = dict(src_dict)
        attributes = []
        _attributes = d.pop("attributes", UNSET)
        for attributes_item_data in (_attributes or []):
            attributes_item = UserProfileAttributeMetadata.from_dict(attributes_item_data)



            attributes.append(attributes_item)


        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in (_groups or []):
            groups_item = UserProfileAttributeGroupMetadata.from_dict(groups_item_data)



            groups.append(groups_item)


        user_profile_metadata = cls(
            attributes=attributes,
            groups=groups,
        )


        user_profile_metadata.additional_properties = d
        return user_profile_metadata

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
