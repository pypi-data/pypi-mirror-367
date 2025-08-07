from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.resource_representation import ResourceRepresentation
  from ..models.policy_representation import PolicyRepresentation





T = TypeVar("T", bound="ScopeRepresentation")



@_attrs_define
class ScopeRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            icon_uri (Union[Unset, str]):
            policies (Union[Unset, list['PolicyRepresentation']]):
            resources (Union[Unset, list['ResourceRepresentation']]):
            display_name (Union[Unset, str]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    icon_uri: Union[Unset, str] = UNSET
    policies: Union[Unset, list['PolicyRepresentation']] = UNSET
    resources: Union[Unset, list['ResourceRepresentation']] = UNSET
    display_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_representation import PolicyRepresentation
        id = self.id

        name = self.name

        icon_uri = self.icon_uri

        policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = []
            for policies_item_data in self.policies:
                policies_item = policies_item_data.to_dict()
                policies.append(policies_item)



        resources: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = []
            for resources_item_data in self.resources:
                resources_item = resources_item_data.to_dict()
                resources.append(resources_item)



        display_name = self.display_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if icon_uri is not UNSET:
            field_dict["iconUri"] = icon_uri
        if policies is not UNSET:
            field_dict["policies"] = policies
        if resources is not UNSET:
            field_dict["resources"] = resources
        if display_name is not UNSET:
            field_dict["displayName"] = display_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_representation import PolicyRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        icon_uri = d.pop("iconUri", UNSET)

        policies = []
        _policies = d.pop("policies", UNSET)
        for policies_item_data in (_policies or []):
            policies_item = PolicyRepresentation.from_dict(policies_item_data)



            policies.append(policies_item)


        resources = []
        _resources = d.pop("resources", UNSET)
        for resources_item_data in (_resources or []):
            resources_item = ResourceRepresentation.from_dict(resources_item_data)



            resources.append(resources_item)


        display_name = d.pop("displayName", UNSET)

        scope_representation = cls(
            id=id,
            name=name,
            icon_uri=icon_uri,
            policies=policies,
            resources=resources,
            display_name=display_name,
        )


        scope_representation.additional_properties = d
        return scope_representation

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
