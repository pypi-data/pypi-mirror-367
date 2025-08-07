from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.event_representation_details import EventRepresentationDetails





T = TypeVar("T", bound="EventRepresentation")



@_attrs_define
class EventRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            time (Union[Unset, int]):
            type_ (Union[Unset, str]):
            realm_id (Union[Unset, str]):
            client_id (Union[Unset, str]):
            user_id (Union[Unset, str]):
            session_id (Union[Unset, str]):
            ip_address (Union[Unset, str]):
            error (Union[Unset, str]):
            details (Union[Unset, EventRepresentationDetails]):
     """

    id: Union[Unset, str] = UNSET
    time: Union[Unset, int] = UNSET
    type_: Union[Unset, str] = UNSET
    realm_id: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    session_id: Union[Unset, str] = UNSET
    ip_address: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    details: Union[Unset, 'EventRepresentationDetails'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.event_representation_details import EventRepresentationDetails
        id = self.id

        time = self.time

        type_ = self.type_

        realm_id = self.realm_id

        client_id = self.client_id

        user_id = self.user_id

        session_id = self.session_id

        ip_address = self.ip_address

        error = self.error

        details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if time is not UNSET:
            field_dict["time"] = time
        if type_ is not UNSET:
            field_dict["type"] = type_
        if realm_id is not UNSET:
            field_dict["realmId"] = realm_id
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if ip_address is not UNSET:
            field_dict["ipAddress"] = ip_address
        if error is not UNSET:
            field_dict["error"] = error
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_representation_details import EventRepresentationDetails
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        time = d.pop("time", UNSET)

        type_ = d.pop("type", UNSET)

        realm_id = d.pop("realmId", UNSET)

        client_id = d.pop("clientId", UNSET)

        user_id = d.pop("userId", UNSET)

        session_id = d.pop("sessionId", UNSET)

        ip_address = d.pop("ipAddress", UNSET)

        error = d.pop("error", UNSET)

        _details = d.pop("details", UNSET)
        details: Union[Unset, EventRepresentationDetails]
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = EventRepresentationDetails.from_dict(_details)




        event_representation = cls(
            id=id,
            time=time,
            type_=type_,
            realm_id=realm_id,
            client_id=client_id,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            error=error,
            details=details,
        )


        event_representation.additional_properties = d
        return event_representation

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
