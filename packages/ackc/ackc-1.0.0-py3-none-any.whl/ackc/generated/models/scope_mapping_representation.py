from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ScopeMappingRepresentation")



@_attrs_define
class ScopeMappingRepresentation:
    """ 
        Attributes:
            self_ (Union[Unset, str]):
            client (Union[Unset, str]):
            client_template (Union[Unset, str]):
            client_scope (Union[Unset, str]):
            roles (Union[Unset, list[str]]):
     """

    self_: Union[Unset, str] = UNSET
    client: Union[Unset, str] = UNSET
    client_template: Union[Unset, str] = UNSET
    client_scope: Union[Unset, str] = UNSET
    roles: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        self_ = self.self_

        client = self.client

        client_template = self.client_template

        client_scope = self.client_scope

        roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if self_ is not UNSET:
            field_dict["self"] = self_
        if client is not UNSET:
            field_dict["client"] = client
        if client_template is not UNSET:
            field_dict["clientTemplate"] = client_template
        if client_scope is not UNSET:
            field_dict["clientScope"] = client_scope
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        self_ = d.pop("self", UNSET)

        client = d.pop("client", UNSET)

        client_template = d.pop("clientTemplate", UNSET)

        client_scope = d.pop("clientScope", UNSET)

        roles = cast(list[str], d.pop("roles", UNSET))


        scope_mapping_representation = cls(
            self_=self_,
            client=client,
            client_template=client_template,
            client_scope=client_scope,
            roles=roles,
        )


        scope_mapping_representation.additional_properties = d
        return scope_mapping_representation

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
