from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.protocol_mapper_representation_config import ProtocolMapperRepresentationConfig





T = TypeVar("T", bound="ProtocolMapperRepresentation")



@_attrs_define
class ProtocolMapperRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            protocol (Union[Unset, str]):
            protocol_mapper (Union[Unset, str]):
            consent_required (Union[Unset, bool]):
            consent_text (Union[Unset, str]):
            config (Union[Unset, ProtocolMapperRepresentationConfig]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    protocol: Union[Unset, str] = UNSET
    protocol_mapper: Union[Unset, str] = UNSET
    consent_required: Union[Unset, bool] = UNSET
    consent_text: Union[Unset, str] = UNSET
    config: Union[Unset, 'ProtocolMapperRepresentationConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.protocol_mapper_representation_config import ProtocolMapperRepresentationConfig
        id = self.id

        name = self.name

        protocol = self.protocol

        protocol_mapper = self.protocol_mapper

        consent_required = self.consent_required

        consent_text = self.consent_text

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
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if protocol_mapper is not UNSET:
            field_dict["protocolMapper"] = protocol_mapper
        if consent_required is not UNSET:
            field_dict["consentRequired"] = consent_required
        if consent_text is not UNSET:
            field_dict["consentText"] = consent_text
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.protocol_mapper_representation_config import ProtocolMapperRepresentationConfig
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        protocol = d.pop("protocol", UNSET)

        protocol_mapper = d.pop("protocolMapper", UNSET)

        consent_required = d.pop("consentRequired", UNSET)

        consent_text = d.pop("consentText", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, ProtocolMapperRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = ProtocolMapperRepresentationConfig.from_dict(_config)




        protocol_mapper_representation = cls(
            id=id,
            name=name,
            protocol=protocol,
            protocol_mapper=protocol_mapper,
            consent_required=consent_required,
            consent_text=consent_text,
            config=config,
        )


        protocol_mapper_representation.additional_properties = d
        return protocol_mapper_representation

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
