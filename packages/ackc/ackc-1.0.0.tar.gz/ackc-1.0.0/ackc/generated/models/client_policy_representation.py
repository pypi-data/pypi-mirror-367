from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_policy_condition_representation import ClientPolicyConditionRepresentation





T = TypeVar("T", bound="ClientPolicyRepresentation")



@_attrs_define
class ClientPolicyRepresentation:
    """ 
        Attributes:
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            enabled (Union[Unset, bool]):
            conditions (Union[Unset, list['ClientPolicyConditionRepresentation']]):
            profiles (Union[Unset, list[str]]):
     """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    conditions: Union[Unset, list['ClientPolicyConditionRepresentation']] = UNSET
    profiles: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_policy_condition_representation import ClientPolicyConditionRepresentation
        name = self.name

        description = self.description

        enabled = self.enabled

        conditions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.conditions, Unset):
            conditions = []
            for conditions_item_data in self.conditions:
                conditions_item = conditions_item_data.to_dict()
                conditions.append(conditions_item)



        profiles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.profiles, Unset):
            profiles = self.profiles




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if conditions is not UNSET:
            field_dict["conditions"] = conditions
        if profiles is not UNSET:
            field_dict["profiles"] = profiles

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_policy_condition_representation import ClientPolicyConditionRepresentation
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        enabled = d.pop("enabled", UNSET)

        conditions = []
        _conditions = d.pop("conditions", UNSET)
        for conditions_item_data in (_conditions or []):
            conditions_item = ClientPolicyConditionRepresentation.from_dict(conditions_item_data)



            conditions.append(conditions_item)


        profiles = cast(list[str], d.pop("profiles", UNSET))


        client_policy_representation = cls(
            name=name,
            description=description,
            enabled=enabled,
            conditions=conditions,
            profiles=profiles,
        )


        client_policy_representation.additional_properties = d
        return client_policy_representation

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
