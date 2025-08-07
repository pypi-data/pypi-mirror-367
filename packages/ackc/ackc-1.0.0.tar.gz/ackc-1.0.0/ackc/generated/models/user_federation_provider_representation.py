from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_federation_provider_representation_config import UserFederationProviderRepresentationConfig





T = TypeVar("T", bound="UserFederationProviderRepresentation")



@_attrs_define
class UserFederationProviderRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            display_name (Union[Unset, str]):
            provider_name (Union[Unset, str]):
            config (Union[Unset, UserFederationProviderRepresentationConfig]):
            priority (Union[Unset, int]):
            full_sync_period (Union[Unset, int]):
            changed_sync_period (Union[Unset, int]):
            last_sync (Union[Unset, int]):
     """

    id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    provider_name: Union[Unset, str] = UNSET
    config: Union[Unset, 'UserFederationProviderRepresentationConfig'] = UNSET
    priority: Union[Unset, int] = UNSET
    full_sync_period: Union[Unset, int] = UNSET
    changed_sync_period: Union[Unset, int] = UNSET
    last_sync: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_federation_provider_representation_config import UserFederationProviderRepresentationConfig
        id = self.id

        display_name = self.display_name

        provider_name = self.provider_name

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        priority = self.priority

        full_sync_period = self.full_sync_period

        changed_sync_period = self.changed_sync_period

        last_sync = self.last_sync


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if provider_name is not UNSET:
            field_dict["providerName"] = provider_name
        if config is not UNSET:
            field_dict["config"] = config
        if priority is not UNSET:
            field_dict["priority"] = priority
        if full_sync_period is not UNSET:
            field_dict["fullSyncPeriod"] = full_sync_period
        if changed_sync_period is not UNSET:
            field_dict["changedSyncPeriod"] = changed_sync_period
        if last_sync is not UNSET:
            field_dict["lastSync"] = last_sync

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_federation_provider_representation_config import UserFederationProviderRepresentationConfig
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        display_name = d.pop("displayName", UNSET)

        provider_name = d.pop("providerName", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, UserFederationProviderRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = UserFederationProviderRepresentationConfig.from_dict(_config)




        priority = d.pop("priority", UNSET)

        full_sync_period = d.pop("fullSyncPeriod", UNSET)

        changed_sync_period = d.pop("changedSyncPeriod", UNSET)

        last_sync = d.pop("lastSync", UNSET)

        user_federation_provider_representation = cls(
            id=id,
            display_name=display_name,
            provider_name=provider_name,
            config=config,
            priority=priority,
            full_sync_period=full_sync_period,
            changed_sync_period=changed_sync_period,
            last_sync=last_sync,
        )


        user_federation_provider_representation.additional_properties = d
        return user_federation_provider_representation

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
