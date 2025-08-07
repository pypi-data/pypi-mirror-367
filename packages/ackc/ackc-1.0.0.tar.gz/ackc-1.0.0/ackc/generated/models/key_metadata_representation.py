from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.key_use import KeyUse
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="KeyMetadataRepresentation")



@_attrs_define
class KeyMetadataRepresentation:
    """ 
        Attributes:
            provider_id (Union[Unset, str]):
            provider_priority (Union[Unset, int]):
            kid (Union[Unset, str]):
            status (Union[Unset, str]):
            type_ (Union[Unset, str]):
            algorithm (Union[Unset, str]):
            public_key (Union[Unset, str]):
            certificate (Union[Unset, str]):
            use (Union[Unset, KeyUse]):
            valid_to (Union[Unset, int]):
     """

    provider_id: Union[Unset, str] = UNSET
    provider_priority: Union[Unset, int] = UNSET
    kid: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    algorithm: Union[Unset, str] = UNSET
    public_key: Union[Unset, str] = UNSET
    certificate: Union[Unset, str] = UNSET
    use: Union[Unset, KeyUse] = UNSET
    valid_to: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        provider_id = self.provider_id

        provider_priority = self.provider_priority

        kid = self.kid

        status = self.status

        type_ = self.type_

        algorithm = self.algorithm

        public_key = self.public_key

        certificate = self.certificate

        use: Union[Unset, str] = UNSET
        if not isinstance(self.use, Unset):
            use = self.use.value


        valid_to = self.valid_to


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if provider_id is not UNSET:
            field_dict["providerId"] = provider_id
        if provider_priority is not UNSET:
            field_dict["providerPriority"] = provider_priority
        if kid is not UNSET:
            field_dict["kid"] = kid
        if status is not UNSET:
            field_dict["status"] = status
        if type_ is not UNSET:
            field_dict["type"] = type_
        if algorithm is not UNSET:
            field_dict["algorithm"] = algorithm
        if public_key is not UNSET:
            field_dict["publicKey"] = public_key
        if certificate is not UNSET:
            field_dict["certificate"] = certificate
        if use is not UNSET:
            field_dict["use"] = use
        if valid_to is not UNSET:
            field_dict["validTo"] = valid_to

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_id = d.pop("providerId", UNSET)

        provider_priority = d.pop("providerPriority", UNSET)

        kid = d.pop("kid", UNSET)

        status = d.pop("status", UNSET)

        type_ = d.pop("type", UNSET)

        algorithm = d.pop("algorithm", UNSET)

        public_key = d.pop("publicKey", UNSET)

        certificate = d.pop("certificate", UNSET)

        _use = d.pop("use", UNSET)
        use: Union[Unset, KeyUse]
        if isinstance(_use,  Unset):
            use = UNSET
        else:
            use = KeyUse(_use)




        valid_to = d.pop("validTo", UNSET)

        key_metadata_representation = cls(
            provider_id=provider_id,
            provider_priority=provider_priority,
            kid=kid,
            status=status,
            type_=type_,
            algorithm=algorithm,
            public_key=public_key,
            certificate=certificate,
            use=use,
            valid_to=valid_to,
        )


        key_metadata_representation.additional_properties = d
        return key_metadata_representation

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
