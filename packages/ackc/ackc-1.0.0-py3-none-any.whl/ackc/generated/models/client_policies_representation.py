from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_policy_representation import ClientPolicyRepresentation





T = TypeVar("T", bound="ClientPoliciesRepresentation")



@_attrs_define
class ClientPoliciesRepresentation:
    """ 
        Attributes:
            policies (Union[Unset, list['ClientPolicyRepresentation']]):
            global_policies (Union[Unset, list['ClientPolicyRepresentation']]):
     """

    policies: Union[Unset, list['ClientPolicyRepresentation']] = UNSET
    global_policies: Union[Unset, list['ClientPolicyRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_policy_representation import ClientPolicyRepresentation
        policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = []
            for policies_item_data in self.policies:
                policies_item = policies_item_data.to_dict()
                policies.append(policies_item)



        global_policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.global_policies, Unset):
            global_policies = []
            for global_policies_item_data in self.global_policies:
                global_policies_item = global_policies_item_data.to_dict()
                global_policies.append(global_policies_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if policies is not UNSET:
            field_dict["policies"] = policies
        if global_policies is not UNSET:
            field_dict["globalPolicies"] = global_policies

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_policy_representation import ClientPolicyRepresentation
        d = dict(src_dict)
        policies = []
        _policies = d.pop("policies", UNSET)
        for policies_item_data in (_policies or []):
            policies_item = ClientPolicyRepresentation.from_dict(policies_item_data)



            policies.append(policies_item)


        global_policies = []
        _global_policies = d.pop("globalPolicies", UNSET)
        for global_policies_item_data in (_global_policies or []):
            global_policies_item = ClientPolicyRepresentation.from_dict(global_policies_item_data)



            global_policies.append(global_policies_item)


        client_policies_representation = cls(
            policies=policies,
            global_policies=global_policies,
        )


        client_policies_representation.additional_properties = d
        return client_policies_representation

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
