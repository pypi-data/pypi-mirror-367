from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="FederatedIdentityRepresentation")



@_attrs_define
class FederatedIdentityRepresentation:
    """ 
        Attributes:
            identity_provider (Union[Unset, str]):
            user_id (Union[Unset, str]):
            user_name (Union[Unset, str]):
     """

    identity_provider: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    user_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        identity_provider = self.identity_provider

        user_id = self.user_id

        user_name = self.user_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if identity_provider is not UNSET:
            field_dict["identityProvider"] = identity_provider
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if user_name is not UNSET:
            field_dict["userName"] = user_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identity_provider = d.pop("identityProvider", UNSET)

        user_id = d.pop("userId", UNSET)

        user_name = d.pop("userName", UNSET)

        federated_identity_representation = cls(
            identity_provider=identity_provider,
            user_id=user_id,
            user_name=user_name,
        )


        federated_identity_representation.additional_properties = d
        return federated_identity_representation

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
