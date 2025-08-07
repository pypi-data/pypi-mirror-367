from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="AuthenticationExecutionInfoRepresentation")



@_attrs_define
class AuthenticationExecutionInfoRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            requirement (Union[Unset, str]):
            display_name (Union[Unset, str]):
            alias (Union[Unset, str]):
            description (Union[Unset, str]):
            requirement_choices (Union[Unset, list[str]]):
            configurable (Union[Unset, bool]):
            authentication_flow (Union[Unset, bool]):
            provider_id (Union[Unset, str]):
            authentication_config (Union[Unset, str]):
            flow_id (Union[Unset, str]):
            level (Union[Unset, int]):
            index (Union[Unset, int]):
            priority (Union[Unset, int]):
     """

    id: Union[Unset, str] = UNSET
    requirement: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    alias: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    requirement_choices: Union[Unset, list[str]] = UNSET
    configurable: Union[Unset, bool] = UNSET
    authentication_flow: Union[Unset, bool] = UNSET
    provider_id: Union[Unset, str] = UNSET
    authentication_config: Union[Unset, str] = UNSET
    flow_id: Union[Unset, str] = UNSET
    level: Union[Unset, int] = UNSET
    index: Union[Unset, int] = UNSET
    priority: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        requirement = self.requirement

        display_name = self.display_name

        alias = self.alias

        description = self.description

        requirement_choices: Union[Unset, list[str]] = UNSET
        if not isinstance(self.requirement_choices, Unset):
            requirement_choices = self.requirement_choices



        configurable = self.configurable

        authentication_flow = self.authentication_flow

        provider_id = self.provider_id

        authentication_config = self.authentication_config

        flow_id = self.flow_id

        level = self.level

        index = self.index

        priority = self.priority


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if requirement is not UNSET:
            field_dict["requirement"] = requirement
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if alias is not UNSET:
            field_dict["alias"] = alias
        if description is not UNSET:
            field_dict["description"] = description
        if requirement_choices is not UNSET:
            field_dict["requirementChoices"] = requirement_choices
        if configurable is not UNSET:
            field_dict["configurable"] = configurable
        if authentication_flow is not UNSET:
            field_dict["authenticationFlow"] = authentication_flow
        if provider_id is not UNSET:
            field_dict["providerId"] = provider_id
        if authentication_config is not UNSET:
            field_dict["authenticationConfig"] = authentication_config
        if flow_id is not UNSET:
            field_dict["flowId"] = flow_id
        if level is not UNSET:
            field_dict["level"] = level
        if index is not UNSET:
            field_dict["index"] = index
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        requirement = d.pop("requirement", UNSET)

        display_name = d.pop("displayName", UNSET)

        alias = d.pop("alias", UNSET)

        description = d.pop("description", UNSET)

        requirement_choices = cast(list[str], d.pop("requirementChoices", UNSET))


        configurable = d.pop("configurable", UNSET)

        authentication_flow = d.pop("authenticationFlow", UNSET)

        provider_id = d.pop("providerId", UNSET)

        authentication_config = d.pop("authenticationConfig", UNSET)

        flow_id = d.pop("flowId", UNSET)

        level = d.pop("level", UNSET)

        index = d.pop("index", UNSET)

        priority = d.pop("priority", UNSET)

        authentication_execution_info_representation = cls(
            id=id,
            requirement=requirement,
            display_name=display_name,
            alias=alias,
            description=description,
            requirement_choices=requirement_choices,
            configurable=configurable,
            authentication_flow=authentication_flow,
            provider_id=provider_id,
            authentication_config=authentication_config,
            flow_id=flow_id,
            level=level,
            index=index,
            priority=priority,
        )


        authentication_execution_info_representation.additional_properties = d
        return authentication_execution_info_representation

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
