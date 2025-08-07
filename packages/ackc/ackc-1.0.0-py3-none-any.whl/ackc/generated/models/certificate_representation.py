from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="CertificateRepresentation")



@_attrs_define
class CertificateRepresentation:
    """ 
        Attributes:
            private_key (Union[Unset, str]):
            public_key (Union[Unset, str]):
            certificate (Union[Unset, str]):
            kid (Union[Unset, str]):
     """

    private_key: Union[Unset, str] = UNSET
    public_key: Union[Unset, str] = UNSET
    certificate: Union[Unset, str] = UNSET
    kid: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        private_key = self.private_key

        public_key = self.public_key

        certificate = self.certificate

        kid = self.kid


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if private_key is not UNSET:
            field_dict["privateKey"] = private_key
        if public_key is not UNSET:
            field_dict["publicKey"] = public_key
        if certificate is not UNSET:
            field_dict["certificate"] = certificate
        if kid is not UNSET:
            field_dict["kid"] = kid

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        private_key = d.pop("privateKey", UNSET)

        public_key = d.pop("publicKey", UNSET)

        certificate = d.pop("certificate", UNSET)

        kid = d.pop("kid", UNSET)

        certificate_representation = cls(
            private_key=private_key,
            public_key=public_key,
            certificate=certificate,
            kid=kid,
        )


        certificate_representation.additional_properties = d
        return certificate_representation

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
