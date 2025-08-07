from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.decision_effect import DecisionEffect
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.policy_representation import PolicyRepresentation





T = TypeVar("T", bound="PolicyResultRepresentation")



@_attrs_define
class PolicyResultRepresentation:
    """ 
        Attributes:
            policy (Union[Unset, PolicyRepresentation]):
            status (Union[Unset, DecisionEffect]):
            associated_policies (Union[Unset, list['PolicyResultRepresentation']]):
            scopes (Union[Unset, list[str]]):
            resource_type (Union[Unset, str]):
     """

    policy: Union[Unset, 'PolicyRepresentation'] = UNSET
    status: Union[Unset, DecisionEffect] = UNSET
    associated_policies: Union[Unset, list['PolicyResultRepresentation']] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    resource_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.policy_representation import PolicyRepresentation
        policy: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy, Unset):
            policy = self.policy.to_dict()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        associated_policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.associated_policies, Unset):
            associated_policies = []
            for associated_policies_item_data in self.associated_policies:
                associated_policies_item = associated_policies_item_data.to_dict()
                associated_policies.append(associated_policies_item)



        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        resource_type = self.resource_type


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if policy is not UNSET:
            field_dict["policy"] = policy
        if status is not UNSET:
            field_dict["status"] = status
        if associated_policies is not UNSET:
            field_dict["associatedPolicies"] = associated_policies
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if resource_type is not UNSET:
            field_dict["resourceType"] = resource_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_representation import PolicyRepresentation
        d = dict(src_dict)
        _policy = d.pop("policy", UNSET)
        policy: Union[Unset, PolicyRepresentation]
        if isinstance(_policy,  Unset):
            policy = UNSET
        else:
            policy = PolicyRepresentation.from_dict(_policy)




        _status = d.pop("status", UNSET)
        status: Union[Unset, DecisionEffect]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = DecisionEffect(_status)




        associated_policies = []
        _associated_policies = d.pop("associatedPolicies", UNSET)
        for associated_policies_item_data in (_associated_policies or []):
            associated_policies_item = PolicyResultRepresentation.from_dict(associated_policies_item_data)



            associated_policies.append(associated_policies_item)


        scopes = cast(list[str], d.pop("scopes", UNSET))


        resource_type = d.pop("resourceType", UNSET)

        policy_result_representation = cls(
            policy=policy,
            status=status,
            associated_policies=associated_policies,
            scopes=scopes,
            resource_type=resource_type,
        )


        policy_result_representation.additional_properties = d
        return policy_result_representation

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
