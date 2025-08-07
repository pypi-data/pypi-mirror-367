from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="AuthenticationExecutionRepresentation")



@_attrs_define
class AuthenticationExecutionRepresentation:
    """ 
        Attributes:
            authenticator_config (Union[Unset, str]):
            authenticator (Union[Unset, str]):
            authenticator_flow (Union[Unset, bool]):
            requirement (Union[Unset, str]):
            priority (Union[Unset, int]):
            autheticator_flow (Union[Unset, bool]):
            id (Union[Unset, str]):
            flow_id (Union[Unset, str]):
            parent_flow (Union[Unset, str]):
     """

    authenticator_config: Union[Unset, str] = UNSET
    authenticator: Union[Unset, str] = UNSET
    authenticator_flow: Union[Unset, bool] = UNSET
    requirement: Union[Unset, str] = UNSET
    priority: Union[Unset, int] = UNSET
    autheticator_flow: Union[Unset, bool] = UNSET
    id: Union[Unset, str] = UNSET
    flow_id: Union[Unset, str] = UNSET
    parent_flow: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        authenticator_config = self.authenticator_config

        authenticator = self.authenticator

        authenticator_flow = self.authenticator_flow

        requirement = self.requirement

        priority = self.priority

        autheticator_flow = self.autheticator_flow

        id = self.id

        flow_id = self.flow_id

        parent_flow = self.parent_flow


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if authenticator_config is not UNSET:
            field_dict["authenticatorConfig"] = authenticator_config
        if authenticator is not UNSET:
            field_dict["authenticator"] = authenticator
        if authenticator_flow is not UNSET:
            field_dict["authenticatorFlow"] = authenticator_flow
        if requirement is not UNSET:
            field_dict["requirement"] = requirement
        if priority is not UNSET:
            field_dict["priority"] = priority
        if autheticator_flow is not UNSET:
            field_dict["autheticatorFlow"] = autheticator_flow
        if id is not UNSET:
            field_dict["id"] = id
        if flow_id is not UNSET:
            field_dict["flowId"] = flow_id
        if parent_flow is not UNSET:
            field_dict["parentFlow"] = parent_flow

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        authenticator_config = d.pop("authenticatorConfig", UNSET)

        authenticator = d.pop("authenticator", UNSET)

        authenticator_flow = d.pop("authenticatorFlow", UNSET)

        requirement = d.pop("requirement", UNSET)

        priority = d.pop("priority", UNSET)

        autheticator_flow = d.pop("autheticatorFlow", UNSET)

        id = d.pop("id", UNSET)

        flow_id = d.pop("flowId", UNSET)

        parent_flow = d.pop("parentFlow", UNSET)

        authentication_execution_representation = cls(
            authenticator_config=authenticator_config,
            authenticator=authenticator,
            authenticator_flow=authenticator_flow,
            requirement=requirement,
            priority=priority,
            autheticator_flow=autheticator_flow,
            id=id,
            flow_id=flow_id,
            parent_flow=parent_flow,
        )


        authentication_execution_representation.additional_properties = d
        return authentication_execution_representation

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
