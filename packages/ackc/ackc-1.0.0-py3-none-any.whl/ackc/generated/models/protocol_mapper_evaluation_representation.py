from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ProtocolMapperEvaluationRepresentation")



@_attrs_define
class ProtocolMapperEvaluationRepresentation:
    """ 
        Attributes:
            mapper_id (Union[Unset, str]):
            mapper_name (Union[Unset, str]):
            container_id (Union[Unset, str]):
            container_name (Union[Unset, str]):
            container_type (Union[Unset, str]):
            protocol_mapper (Union[Unset, str]):
     """

    mapper_id: Union[Unset, str] = UNSET
    mapper_name: Union[Unset, str] = UNSET
    container_id: Union[Unset, str] = UNSET
    container_name: Union[Unset, str] = UNSET
    container_type: Union[Unset, str] = UNSET
    protocol_mapper: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        mapper_id = self.mapper_id

        mapper_name = self.mapper_name

        container_id = self.container_id

        container_name = self.container_name

        container_type = self.container_type

        protocol_mapper = self.protocol_mapper


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if mapper_id is not UNSET:
            field_dict["mapperId"] = mapper_id
        if mapper_name is not UNSET:
            field_dict["mapperName"] = mapper_name
        if container_id is not UNSET:
            field_dict["containerId"] = container_id
        if container_name is not UNSET:
            field_dict["containerName"] = container_name
        if container_type is not UNSET:
            field_dict["containerType"] = container_type
        if protocol_mapper is not UNSET:
            field_dict["protocolMapper"] = protocol_mapper

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mapper_id = d.pop("mapperId", UNSET)

        mapper_name = d.pop("mapperName", UNSET)

        container_id = d.pop("containerId", UNSET)

        container_name = d.pop("containerName", UNSET)

        container_type = d.pop("containerType", UNSET)

        protocol_mapper = d.pop("protocolMapper", UNSET)

        protocol_mapper_evaluation_representation = cls(
            mapper_id=mapper_id,
            mapper_name=mapper_name,
            container_id=container_id,
            container_name=container_name,
            container_type=container_type,
            protocol_mapper=protocol_mapper,
        )


        protocol_mapper_evaluation_representation.additional_properties = d
        return protocol_mapper_evaluation_representation

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
