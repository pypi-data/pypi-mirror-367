from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.authentication_execution_export_representation import AuthenticationExecutionExportRepresentation





T = TypeVar("T", bound="AuthenticationFlowRepresentation")



@_attrs_define
class AuthenticationFlowRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            alias (Union[Unset, str]):
            description (Union[Unset, str]):
            provider_id (Union[Unset, str]):
            top_level (Union[Unset, bool]):
            built_in (Union[Unset, bool]):
            authentication_executions (Union[Unset, list['AuthenticationExecutionExportRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    alias: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    provider_id: Union[Unset, str] = UNSET
    top_level: Union[Unset, bool] = UNSET
    built_in: Union[Unset, bool] = UNSET
    authentication_executions: Union[Unset, list['AuthenticationExecutionExportRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.authentication_execution_export_representation import AuthenticationExecutionExportRepresentation
        id = self.id

        alias = self.alias

        description = self.description

        provider_id = self.provider_id

        top_level = self.top_level

        built_in = self.built_in

        authentication_executions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authentication_executions, Unset):
            authentication_executions = []
            for authentication_executions_item_data in self.authentication_executions:
                authentication_executions_item = authentication_executions_item_data.to_dict()
                authentication_executions.append(authentication_executions_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if alias is not UNSET:
            field_dict["alias"] = alias
        if description is not UNSET:
            field_dict["description"] = description
        if provider_id is not UNSET:
            field_dict["providerId"] = provider_id
        if top_level is not UNSET:
            field_dict["topLevel"] = top_level
        if built_in is not UNSET:
            field_dict["builtIn"] = built_in
        if authentication_executions is not UNSET:
            field_dict["authenticationExecutions"] = authentication_executions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authentication_execution_export_representation import AuthenticationExecutionExportRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        alias = d.pop("alias", UNSET)

        description = d.pop("description", UNSET)

        provider_id = d.pop("providerId", UNSET)

        top_level = d.pop("topLevel", UNSET)

        built_in = d.pop("builtIn", UNSET)

        authentication_executions = []
        _authentication_executions = d.pop("authenticationExecutions", UNSET)
        for authentication_executions_item_data in (_authentication_executions or []):
            authentication_executions_item = AuthenticationExecutionExportRepresentation.from_dict(authentication_executions_item_data)



            authentication_executions.append(authentication_executions_item)


        authentication_flow_representation = cls(
            id=id,
            alias=alias,
            description=description,
            provider_id=provider_id,
            top_level=top_level,
            built_in=built_in,
            authentication_executions=authentication_executions,
        )


        authentication_flow_representation.additional_properties = d
        return authentication_flow_representation

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
