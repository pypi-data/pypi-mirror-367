from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="KeyStoreConfig")



@_attrs_define
class KeyStoreConfig:
    """ 
        Attributes:
            realm_certificate (Union[Unset, bool]):
            store_password (Union[Unset, str]):
            key_password (Union[Unset, str]):
            key_alias (Union[Unset, str]):
            realm_alias (Union[Unset, str]):
            format_ (Union[Unset, str]):
            key_size (Union[Unset, int]):
            validity (Union[Unset, int]):
     """

    realm_certificate: Union[Unset, bool] = UNSET
    store_password: Union[Unset, str] = UNSET
    key_password: Union[Unset, str] = UNSET
    key_alias: Union[Unset, str] = UNSET
    realm_alias: Union[Unset, str] = UNSET
    format_: Union[Unset, str] = UNSET
    key_size: Union[Unset, int] = UNSET
    validity: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        realm_certificate = self.realm_certificate

        store_password = self.store_password

        key_password = self.key_password

        key_alias = self.key_alias

        realm_alias = self.realm_alias

        format_ = self.format_

        key_size = self.key_size

        validity = self.validity


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if realm_certificate is not UNSET:
            field_dict["realmCertificate"] = realm_certificate
        if store_password is not UNSET:
            field_dict["storePassword"] = store_password
        if key_password is not UNSET:
            field_dict["keyPassword"] = key_password
        if key_alias is not UNSET:
            field_dict["keyAlias"] = key_alias
        if realm_alias is not UNSET:
            field_dict["realmAlias"] = realm_alias
        if format_ is not UNSET:
            field_dict["format"] = format_
        if key_size is not UNSET:
            field_dict["keySize"] = key_size
        if validity is not UNSET:
            field_dict["validity"] = validity

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        realm_certificate = d.pop("realmCertificate", UNSET)

        store_password = d.pop("storePassword", UNSET)

        key_password = d.pop("keyPassword", UNSET)

        key_alias = d.pop("keyAlias", UNSET)

        realm_alias = d.pop("realmAlias", UNSET)

        format_ = d.pop("format", UNSET)

        key_size = d.pop("keySize", UNSET)

        validity = d.pop("validity", UNSET)

        key_store_config = cls(
            realm_certificate=realm_certificate,
            store_password=store_password,
            key_password=key_password,
            key_alias=key_alias,
            realm_alias=realm_alias,
            format_=format_,
            key_size=key_size,
            validity=validity,
        )


        key_store_config.additional_properties = d
        return key_store_config

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
