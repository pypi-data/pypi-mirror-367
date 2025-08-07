from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="AuthDetailsRepresentation")



@_attrs_define
class AuthDetailsRepresentation:
    """ 
        Attributes:
            realm_id (Union[Unset, str]):
            client_id (Union[Unset, str]):
            user_id (Union[Unset, str]):
            ip_address (Union[Unset, str]):
     """

    realm_id: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    ip_address: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        realm_id = self.realm_id

        client_id = self.client_id

        user_id = self.user_id

        ip_address = self.ip_address


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if realm_id is not UNSET:
            field_dict["realmId"] = realm_id
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if ip_address is not UNSET:
            field_dict["ipAddress"] = ip_address

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        realm_id = d.pop("realmId", UNSET)

        client_id = d.pop("clientId", UNSET)

        user_id = d.pop("userId", UNSET)

        ip_address = d.pop("ipAddress", UNSET)

        auth_details_representation = cls(
            realm_id=realm_id,
            client_id=client_id,
            user_id=user_id,
            ip_address=ip_address,
        )


        auth_details_representation.additional_properties = d
        return auth_details_representation

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
