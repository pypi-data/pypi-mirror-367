from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.required_action_provider_representation_config import RequiredActionProviderRepresentationConfig





T = TypeVar("T", bound="RequiredActionProviderRepresentation")



@_attrs_define
class RequiredActionProviderRepresentation:
    """ 
        Attributes:
            alias (Union[Unset, str]):
            name (Union[Unset, str]):
            provider_id (Union[Unset, str]):
            enabled (Union[Unset, bool]):
            default_action (Union[Unset, bool]):
            priority (Union[Unset, int]):
            config (Union[Unset, RequiredActionProviderRepresentationConfig]):
     """

    alias: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    provider_id: Union[Unset, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    default_action: Union[Unset, bool] = UNSET
    priority: Union[Unset, int] = UNSET
    config: Union[Unset, 'RequiredActionProviderRepresentationConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.required_action_provider_representation_config import RequiredActionProviderRepresentationConfig
        alias = self.alias

        name = self.name

        provider_id = self.provider_id

        enabled = self.enabled

        default_action = self.default_action

        priority = self.priority

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if alias is not UNSET:
            field_dict["alias"] = alias
        if name is not UNSET:
            field_dict["name"] = name
        if provider_id is not UNSET:
            field_dict["providerId"] = provider_id
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if default_action is not UNSET:
            field_dict["defaultAction"] = default_action
        if priority is not UNSET:
            field_dict["priority"] = priority
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.required_action_provider_representation_config import RequiredActionProviderRepresentationConfig
        d = dict(src_dict)
        alias = d.pop("alias", UNSET)

        name = d.pop("name", UNSET)

        provider_id = d.pop("providerId", UNSET)

        enabled = d.pop("enabled", UNSET)

        default_action = d.pop("defaultAction", UNSET)

        priority = d.pop("priority", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, RequiredActionProviderRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = RequiredActionProviderRepresentationConfig.from_dict(_config)




        required_action_provider_representation = cls(
            alias=alias,
            name=name,
            provider_id=provider_id,
            enabled=enabled,
            default_action=default_action,
            priority=priority,
            config=config,
        )


        required_action_provider_representation.additional_properties = d
        return required_action_provider_representation

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
