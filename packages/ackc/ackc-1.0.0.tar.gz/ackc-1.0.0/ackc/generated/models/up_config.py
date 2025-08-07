from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.unmanaged_attribute_policy import UnmanagedAttributePolicy
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.up_group import UPGroup
  from ..models.up_attribute import UPAttribute





T = TypeVar("T", bound="UPConfig")



@_attrs_define
class UPConfig:
    """ 
        Attributes:
            attributes (Union[Unset, list['UPAttribute']]):
            groups (Union[Unset, list['UPGroup']]):
            unmanaged_attribute_policy (Union[Unset, UnmanagedAttributePolicy]):
     """

    attributes: Union[Unset, list['UPAttribute']] = UNSET
    groups: Union[Unset, list['UPGroup']] = UNSET
    unmanaged_attribute_policy: Union[Unset, UnmanagedAttributePolicy] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.up_group import UPGroup
        from ..models.up_attribute import UPAttribute
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



        unmanaged_attribute_policy: Union[Unset, str] = UNSET
        if not isinstance(self.unmanaged_attribute_policy, Unset):
            unmanaged_attribute_policy = self.unmanaged_attribute_policy.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if groups is not UNSET:
            field_dict["groups"] = groups
        if unmanaged_attribute_policy is not UNSET:
            field_dict["unmanagedAttributePolicy"] = unmanaged_attribute_policy

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.up_group import UPGroup
        from ..models.up_attribute import UPAttribute
        d = dict(src_dict)
        attributes = []
        _attributes = d.pop("attributes", UNSET)
        for attributes_item_data in (_attributes or []):
            attributes_item = UPAttribute.from_dict(attributes_item_data)



            attributes.append(attributes_item)


        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in (_groups or []):
            groups_item = UPGroup.from_dict(groups_item_data)



            groups.append(groups_item)


        _unmanaged_attribute_policy = d.pop("unmanagedAttributePolicy", UNSET)
        unmanaged_attribute_policy: Union[Unset, UnmanagedAttributePolicy]
        if isinstance(_unmanaged_attribute_policy,  Unset):
            unmanaged_attribute_policy = UNSET
        else:
            unmanaged_attribute_policy = UnmanagedAttributePolicy(_unmanaged_attribute_policy)




        up_config = cls(
            attributes=attributes,
            groups=groups,
            unmanaged_attribute_policy=unmanaged_attribute_policy,
        )


        up_config.additional_properties = d
        return up_config

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
