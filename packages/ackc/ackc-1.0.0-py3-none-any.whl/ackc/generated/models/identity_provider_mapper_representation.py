from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.identity_provider_mapper_representation_config import IdentityProviderMapperRepresentationConfig





T = TypeVar("T", bound="IdentityProviderMapperRepresentation")



@_attrs_define
class IdentityProviderMapperRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            identity_provider_alias (Union[Unset, str]):
            identity_provider_mapper (Union[Unset, str]):
            config (Union[Unset, IdentityProviderMapperRepresentationConfig]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    identity_provider_alias: Union[Unset, str] = UNSET
    identity_provider_mapper: Union[Unset, str] = UNSET
    config: Union[Unset, 'IdentityProviderMapperRepresentationConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.identity_provider_mapper_representation_config import IdentityProviderMapperRepresentationConfig
        id = self.id

        name = self.name

        identity_provider_alias = self.identity_provider_alias

        identity_provider_mapper = self.identity_provider_mapper

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
        if identity_provider_alias is not UNSET:
            field_dict["identityProviderAlias"] = identity_provider_alias
        if identity_provider_mapper is not UNSET:
            field_dict["identityProviderMapper"] = identity_provider_mapper
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identity_provider_mapper_representation_config import IdentityProviderMapperRepresentationConfig
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        identity_provider_alias = d.pop("identityProviderAlias", UNSET)

        identity_provider_mapper = d.pop("identityProviderMapper", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, IdentityProviderMapperRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = IdentityProviderMapperRepresentationConfig.from_dict(_config)




        identity_provider_mapper_representation = cls(
            id=id,
            name=name,
            identity_provider_alias=identity_provider_alias,
            identity_provider_mapper=identity_provider_mapper,
            config=config,
        )


        identity_provider_mapper_representation.additional_properties = d
        return identity_provider_mapper_representation

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
