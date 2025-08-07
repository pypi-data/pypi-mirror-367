from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString





T = TypeVar("T", bound="CredentialRepresentation")



@_attrs_define
class CredentialRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            type_ (Union[Unset, str]):
            user_label (Union[Unset, str]):
            created_date (Union[Unset, int]):
            secret_data (Union[Unset, str]):
            credential_data (Union[Unset, str]):
            priority (Union[Unset, int]):
            value (Union[Unset, str]):
            temporary (Union[Unset, bool]):
            device (Union[Unset, str]):
            hashed_salted_value (Union[Unset, str]):
            salt (Union[Unset, str]):
            hash_iterations (Union[Unset, int]):
            counter (Union[Unset, int]):
            algorithm (Union[Unset, str]):
            digits (Union[Unset, int]):
            period (Union[Unset, int]):
            config (Union[Unset, MultivaluedHashMapStringString]):
            federation_link (Union[Unset, str]):
     """

    id: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    user_label: Union[Unset, str] = UNSET
    created_date: Union[Unset, int] = UNSET
    secret_data: Union[Unset, str] = UNSET
    credential_data: Union[Unset, str] = UNSET
    priority: Union[Unset, int] = UNSET
    value: Union[Unset, str] = UNSET
    temporary: Union[Unset, bool] = UNSET
    device: Union[Unset, str] = UNSET
    hashed_salted_value: Union[Unset, str] = UNSET
    salt: Union[Unset, str] = UNSET
    hash_iterations: Union[Unset, int] = UNSET
    counter: Union[Unset, int] = UNSET
    algorithm: Union[Unset, str] = UNSET
    digits: Union[Unset, int] = UNSET
    period: Union[Unset, int] = UNSET
    config: Union[Unset, 'MultivaluedHashMapStringString'] = UNSET
    federation_link: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString
        id = self.id

        type_ = self.type_

        user_label = self.user_label

        created_date = self.created_date

        secret_data = self.secret_data

        credential_data = self.credential_data

        priority = self.priority

        value = self.value

        temporary = self.temporary

        device = self.device

        hashed_salted_value = self.hashed_salted_value

        salt = self.salt

        hash_iterations = self.hash_iterations

        counter = self.counter

        algorithm = self.algorithm

        digits = self.digits

        period = self.period

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        federation_link = self.federation_link


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if user_label is not UNSET:
            field_dict["userLabel"] = user_label
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if secret_data is not UNSET:
            field_dict["secretData"] = secret_data
        if credential_data is not UNSET:
            field_dict["credentialData"] = credential_data
        if priority is not UNSET:
            field_dict["priority"] = priority
        if value is not UNSET:
            field_dict["value"] = value
        if temporary is not UNSET:
            field_dict["temporary"] = temporary
        if device is not UNSET:
            field_dict["device"] = device
        if hashed_salted_value is not UNSET:
            field_dict["hashedSaltedValue"] = hashed_salted_value
        if salt is not UNSET:
            field_dict["salt"] = salt
        if hash_iterations is not UNSET:
            field_dict["hashIterations"] = hash_iterations
        if counter is not UNSET:
            field_dict["counter"] = counter
        if algorithm is not UNSET:
            field_dict["algorithm"] = algorithm
        if digits is not UNSET:
            field_dict["digits"] = digits
        if period is not UNSET:
            field_dict["period"] = period
        if config is not UNSET:
            field_dict["config"] = config
        if federation_link is not UNSET:
            field_dict["federationLink"] = federation_link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.multivalued_hash_map_string_string import MultivaluedHashMapStringString
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        type_ = d.pop("type", UNSET)

        user_label = d.pop("userLabel", UNSET)

        created_date = d.pop("createdDate", UNSET)

        secret_data = d.pop("secretData", UNSET)

        credential_data = d.pop("credentialData", UNSET)

        priority = d.pop("priority", UNSET)

        value = d.pop("value", UNSET)

        temporary = d.pop("temporary", UNSET)

        device = d.pop("device", UNSET)

        hashed_salted_value = d.pop("hashedSaltedValue", UNSET)

        salt = d.pop("salt", UNSET)

        hash_iterations = d.pop("hashIterations", UNSET)

        counter = d.pop("counter", UNSET)

        algorithm = d.pop("algorithm", UNSET)

        digits = d.pop("digits", UNSET)

        period = d.pop("period", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, MultivaluedHashMapStringString]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = MultivaluedHashMapStringString.from_dict(_config)




        federation_link = d.pop("federationLink", UNSET)

        credential_representation = cls(
            id=id,
            type_=type_,
            user_label=user_label,
            created_date=created_date,
            secret_data=secret_data,
            credential_data=credential_data,
            priority=priority,
            value=value,
            temporary=temporary,
            device=device,
            hashed_salted_value=hashed_salted_value,
            salt=salt,
            hash_iterations=hash_iterations,
            counter=counter,
            algorithm=algorithm,
            digits=digits,
            period=period,
            config=config,
            federation_link=federation_link,
        )


        credential_representation.additional_properties = d
        return credential_representation

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
