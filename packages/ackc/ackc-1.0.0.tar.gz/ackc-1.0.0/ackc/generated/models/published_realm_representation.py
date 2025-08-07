from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PublishedRealmRepresentation")



@_attrs_define
class PublishedRealmRepresentation:
    """ 
        Attributes:
            realm (Union[Unset, str]):
            public_key (Union[Unset, str]):
            token_service (Union[Unset, str]):
            account_service (Union[Unset, str]):
            tokens_not_before (Union[Unset, int]):
     """

    realm: Union[Unset, str] = UNSET
    public_key: Union[Unset, str] = UNSET
    token_service: Union[Unset, str] = UNSET
    account_service: Union[Unset, str] = UNSET
    tokens_not_before: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        realm = self.realm

        public_key = self.public_key

        token_service = self.token_service

        account_service = self.account_service

        tokens_not_before = self.tokens_not_before


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if realm is not UNSET:
            field_dict["realm"] = realm
        if public_key is not UNSET:
            field_dict["public_key"] = public_key
        if token_service is not UNSET:
            field_dict["token-service"] = token_service
        if account_service is not UNSET:
            field_dict["account-service"] = account_service
        if tokens_not_before is not UNSET:
            field_dict["tokens-not-before"] = tokens_not_before

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        realm = d.pop("realm", UNSET)

        public_key = d.pop("public_key", UNSET)

        token_service = d.pop("token-service", UNSET)

        account_service = d.pop("account-service", UNSET)

        tokens_not_before = d.pop("tokens-not-before", UNSET)

        published_realm_representation = cls(
            realm=realm,
            public_key=public_key,
            token_service=token_service,
            account_service=account_service,
            tokens_not_before=tokens_not_before,
        )


        published_realm_representation.additional_properties = d
        return published_realm_representation

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
