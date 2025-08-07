from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_type_representation_config import ClientTypeRepresentationConfig





T = TypeVar("T", bound="ClientTypeRepresentation")



@_attrs_define
class ClientTypeRepresentation:
    """ 
        Attributes:
            name (Union[Unset, str]):
            provider (Union[Unset, str]):
            parent (Union[Unset, str]):
            config (Union[Unset, ClientTypeRepresentationConfig]):
     """

    name: Union[Unset, str] = UNSET
    provider: Union[Unset, str] = UNSET
    parent: Union[Unset, str] = UNSET
    config: Union[Unset, 'ClientTypeRepresentationConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_type_representation_config import ClientTypeRepresentationConfig
        name = self.name

        provider = self.provider

        parent = self.parent

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if provider is not UNSET:
            field_dict["provider"] = provider
        if parent is not UNSET:
            field_dict["parent"] = parent
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_type_representation_config import ClientTypeRepresentationConfig
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        provider = d.pop("provider", UNSET)

        parent = d.pop("parent", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, ClientTypeRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = ClientTypeRepresentationConfig.from_dict(_config)




        client_type_representation = cls(
            name=name,
            provider=provider,
            parent=parent,
            config=config,
        )


        client_type_representation.additional_properties = d
        return client_type_representation

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
