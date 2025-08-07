from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ClaimRepresentation")



@_attrs_define
class ClaimRepresentation:
    """ 
        Attributes:
            name (Union[Unset, bool]):
            username (Union[Unset, bool]):
            profile (Union[Unset, bool]):
            picture (Union[Unset, bool]):
            website (Union[Unset, bool]):
            email (Union[Unset, bool]):
            gender (Union[Unset, bool]):
            locale (Union[Unset, bool]):
            address (Union[Unset, bool]):
            phone (Union[Unset, bool]):
     """

    name: Union[Unset, bool] = UNSET
    username: Union[Unset, bool] = UNSET
    profile: Union[Unset, bool] = UNSET
    picture: Union[Unset, bool] = UNSET
    website: Union[Unset, bool] = UNSET
    email: Union[Unset, bool] = UNSET
    gender: Union[Unset, bool] = UNSET
    locale: Union[Unset, bool] = UNSET
    address: Union[Unset, bool] = UNSET
    phone: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        username = self.username

        profile = self.profile

        picture = self.picture

        website = self.website

        email = self.email

        gender = self.gender

        locale = self.locale

        address = self.address

        phone = self.phone


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if username is not UNSET:
            field_dict["username"] = username
        if profile is not UNSET:
            field_dict["profile"] = profile
        if picture is not UNSET:
            field_dict["picture"] = picture
        if website is not UNSET:
            field_dict["website"] = website
        if email is not UNSET:
            field_dict["email"] = email
        if gender is not UNSET:
            field_dict["gender"] = gender
        if locale is not UNSET:
            field_dict["locale"] = locale
        if address is not UNSET:
            field_dict["address"] = address
        if phone is not UNSET:
            field_dict["phone"] = phone

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        username = d.pop("username", UNSET)

        profile = d.pop("profile", UNSET)

        picture = d.pop("picture", UNSET)

        website = d.pop("website", UNSET)

        email = d.pop("email", UNSET)

        gender = d.pop("gender", UNSET)

        locale = d.pop("locale", UNSET)

        address = d.pop("address", UNSET)

        phone = d.pop("phone", UNSET)

        claim_representation = cls(
            name=name,
            username=username,
            profile=profile,
            picture=picture,
            website=website,
            email=email,
            gender=gender,
            locale=locale,
            address=address,
            phone=phone,
        )


        claim_representation.additional_properties = d
        return claim_representation

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
