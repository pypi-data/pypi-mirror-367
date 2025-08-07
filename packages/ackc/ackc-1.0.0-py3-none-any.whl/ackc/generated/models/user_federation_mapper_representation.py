from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_federation_mapper_representation_config import UserFederationMapperRepresentationConfig





T = TypeVar("T", bound="UserFederationMapperRepresentation")



@_attrs_define
class UserFederationMapperRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            federation_provider_display_name (Union[Unset, str]):
            federation_mapper_type (Union[Unset, str]):
            config (Union[Unset, UserFederationMapperRepresentationConfig]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    federation_provider_display_name: Union[Unset, str] = UNSET
    federation_mapper_type: Union[Unset, str] = UNSET
    config: Union[Unset, 'UserFederationMapperRepresentationConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_federation_mapper_representation_config import UserFederationMapperRepresentationConfig
        id = self.id

        name = self.name

        federation_provider_display_name = self.federation_provider_display_name

        federation_mapper_type = self.federation_mapper_type

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if federation_provider_display_name is not UNSET:
            field_dict["federationProviderDisplayName"] = federation_provider_display_name
        if federation_mapper_type is not UNSET:
            field_dict["federationMapperType"] = federation_mapper_type
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_federation_mapper_representation_config import UserFederationMapperRepresentationConfig
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        federation_provider_display_name = d.pop("federationProviderDisplayName", UNSET)

        federation_mapper_type = d.pop("federationMapperType", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, UserFederationMapperRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = UserFederationMapperRepresentationConfig.from_dict(_config)




        user_federation_mapper_representation = cls(
            id=id,
            name=name,
            federation_provider_display_name=federation_provider_display_name,
            federation_mapper_type=federation_mapper_type,
            config=config,
        )


        user_federation_mapper_representation.additional_properties = d
        return user_federation_mapper_representation

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
