from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ClientInitialAccessPresentation")



@_attrs_define
class ClientInitialAccessPresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            token (Union[Unset, str]):
            timestamp (Union[Unset, int]):
            expiration (Union[Unset, int]):
            count (Union[Unset, int]):
            remaining_count (Union[Unset, int]):
     """

    id: Union[Unset, str] = UNSET
    token: Union[Unset, str] = UNSET
    timestamp: Union[Unset, int] = UNSET
    expiration: Union[Unset, int] = UNSET
    count: Union[Unset, int] = UNSET
    remaining_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        token = self.token

        timestamp = self.timestamp

        expiration = self.expiration

        count = self.count

        remaining_count = self.remaining_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if token is not UNSET:
            field_dict["token"] = token
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if expiration is not UNSET:
            field_dict["expiration"] = expiration
        if count is not UNSET:
            field_dict["count"] = count
        if remaining_count is not UNSET:
            field_dict["remainingCount"] = remaining_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        token = d.pop("token", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        expiration = d.pop("expiration", UNSET)

        count = d.pop("count", UNSET)

        remaining_count = d.pop("remainingCount", UNSET)

        client_initial_access_presentation = cls(
            id=id,
            token=token,
            timestamp=timestamp,
            expiration=expiration,
            count=count,
            remaining_count=remaining_count,
        )


        client_initial_access_presentation.additional_properties = d
        return client_initial_access_presentation

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
