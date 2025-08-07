from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="RealmEventsConfigRepresentation")



@_attrs_define
class RealmEventsConfigRepresentation:
    """ 
        Attributes:
            events_enabled (Union[Unset, bool]):
            events_expiration (Union[Unset, int]):
            events_listeners (Union[Unset, list[str]]):
            enabled_event_types (Union[Unset, list[str]]):
            admin_events_enabled (Union[Unset, bool]):
            admin_events_details_enabled (Union[Unset, bool]):
     """

    events_enabled: Union[Unset, bool] = UNSET
    events_expiration: Union[Unset, int] = UNSET
    events_listeners: Union[Unset, list[str]] = UNSET
    enabled_event_types: Union[Unset, list[str]] = UNSET
    admin_events_enabled: Union[Unset, bool] = UNSET
    admin_events_details_enabled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        events_enabled = self.events_enabled

        events_expiration = self.events_expiration

        events_listeners: Union[Unset, list[str]] = UNSET
        if not isinstance(self.events_listeners, Unset):
            events_listeners = self.events_listeners



        enabled_event_types: Union[Unset, list[str]] = UNSET
        if not isinstance(self.enabled_event_types, Unset):
            enabled_event_types = self.enabled_event_types



        admin_events_enabled = self.admin_events_enabled

        admin_events_details_enabled = self.admin_events_details_enabled


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if events_enabled is not UNSET:
            field_dict["eventsEnabled"] = events_enabled
        if events_expiration is not UNSET:
            field_dict["eventsExpiration"] = events_expiration
        if events_listeners is not UNSET:
            field_dict["eventsListeners"] = events_listeners
        if enabled_event_types is not UNSET:
            field_dict["enabledEventTypes"] = enabled_event_types
        if admin_events_enabled is not UNSET:
            field_dict["adminEventsEnabled"] = admin_events_enabled
        if admin_events_details_enabled is not UNSET:
            field_dict["adminEventsDetailsEnabled"] = admin_events_details_enabled

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        events_enabled = d.pop("eventsEnabled", UNSET)

        events_expiration = d.pop("eventsExpiration", UNSET)

        events_listeners = cast(list[str], d.pop("eventsListeners", UNSET))


        enabled_event_types = cast(list[str], d.pop("enabledEventTypes", UNSET))


        admin_events_enabled = d.pop("adminEventsEnabled", UNSET)

        admin_events_details_enabled = d.pop("adminEventsDetailsEnabled", UNSET)

        realm_events_config_representation = cls(
            events_enabled=events_enabled,
            events_expiration=events_expiration,
            events_listeners=events_listeners,
            enabled_event_types=enabled_event_types,
            admin_events_enabled=admin_events_enabled,
            admin_events_details_enabled=admin_events_details_enabled,
        )


        realm_events_config_representation.additional_properties = d
        return realm_events_config_representation

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
