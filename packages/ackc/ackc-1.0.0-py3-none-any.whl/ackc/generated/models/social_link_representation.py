from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="SocialLinkRepresentation")



@_attrs_define
class SocialLinkRepresentation:
    """ 
        Attributes:
            social_provider (Union[Unset, str]):
            social_user_id (Union[Unset, str]):
            social_username (Union[Unset, str]):
     """

    social_provider: Union[Unset, str] = UNSET
    social_user_id: Union[Unset, str] = UNSET
    social_username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        social_provider = self.social_provider

        social_user_id = self.social_user_id

        social_username = self.social_username


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if social_provider is not UNSET:
            field_dict["socialProvider"] = social_provider
        if social_user_id is not UNSET:
            field_dict["socialUserId"] = social_user_id
        if social_username is not UNSET:
            field_dict["socialUsername"] = social_username

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        social_provider = d.pop("socialProvider", UNSET)

        social_user_id = d.pop("socialUserId", UNSET)

        social_username = d.pop("socialUsername", UNSET)

        social_link_representation = cls(
            social_provider=social_provider,
            social_user_id=social_user_id,
            social_username=social_username,
        )


        social_link_representation.additional_properties = d
        return social_link_representation

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
