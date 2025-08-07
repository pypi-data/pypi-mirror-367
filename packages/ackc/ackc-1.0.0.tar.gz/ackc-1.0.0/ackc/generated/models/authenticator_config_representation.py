from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.authenticator_config_representation_config import AuthenticatorConfigRepresentationConfig





T = TypeVar("T", bound="AuthenticatorConfigRepresentation")



@_attrs_define
class AuthenticatorConfigRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            alias (Union[Unset, str]):
            config (Union[Unset, AuthenticatorConfigRepresentationConfig]):
     """

    id: Union[Unset, str] = UNSET
    alias: Union[Unset, str] = UNSET
    config: Union[Unset, 'AuthenticatorConfigRepresentationConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.authenticator_config_representation_config import AuthenticatorConfigRepresentationConfig
        id = self.id

        alias = self.alias

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if alias is not UNSET:
            field_dict["alias"] = alias
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authenticator_config_representation_config import AuthenticatorConfigRepresentationConfig
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        alias = d.pop("alias", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, AuthenticatorConfigRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = AuthenticatorConfigRepresentationConfig.from_dict(_config)




        authenticator_config_representation = cls(
            id=id,
            alias=alias,
            config=config,
        )


        authenticator_config_representation.additional_properties = d
        return authenticator_config_representation

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
