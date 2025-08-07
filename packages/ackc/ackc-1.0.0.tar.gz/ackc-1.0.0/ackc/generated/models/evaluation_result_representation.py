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
  from ..models.scope_representation import ScopeRepresentation
  from ..models.resource_representation import ResourceRepresentation
  from ..models.policy_result_representation import PolicyResultRepresentation





T = TypeVar("T", bound="EvaluationResultRepresentation")



@_attrs_define
class EvaluationResultRepresentation:
    """ 
        Attributes:
            resource (Union[Unset, ResourceRepresentation]):
            scopes (Union[Unset, list['ScopeRepresentation']]):
            policies (Union[Unset, list['PolicyResultRepresentation']]):
            status (Union[Unset, DecisionEffect]):
            allowed_scopes (Union[Unset, list['ScopeRepresentation']]):
            denied_scopes (Union[Unset, list['ScopeRepresentation']]):
     """

    resource: Union[Unset, 'ResourceRepresentation'] = UNSET
    scopes: Union[Unset, list['ScopeRepresentation']] = UNSET
    policies: Union[Unset, list['PolicyResultRepresentation']] = UNSET
    status: Union[Unset, DecisionEffect] = UNSET
    allowed_scopes: Union[Unset, list['ScopeRepresentation']] = UNSET
    denied_scopes: Union[Unset, list['ScopeRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_result_representation import PolicyResultRepresentation
        resource: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.resource, Unset):
            resource = self.resource.to_dict()

        scopes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = []
            for scopes_item_data in self.scopes:
                scopes_item = scopes_item_data.to_dict()
                scopes.append(scopes_item)



        policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = []
            for policies_item_data in self.policies:
                policies_item = policies_item_data.to_dict()
                policies.append(policies_item)



        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        allowed_scopes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.allowed_scopes, Unset):
            allowed_scopes = []
            for allowed_scopes_item_data in self.allowed_scopes:
                allowed_scopes_item = allowed_scopes_item_data.to_dict()
                allowed_scopes.append(allowed_scopes_item)



        denied_scopes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.denied_scopes, Unset):
            denied_scopes = []
            for denied_scopes_item_data in self.denied_scopes:
                denied_scopes_item = denied_scopes_item_data.to_dict()
                denied_scopes.append(denied_scopes_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if resource is not UNSET:
            field_dict["resource"] = resource
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if policies is not UNSET:
            field_dict["policies"] = policies
        if status is not UNSET:
            field_dict["status"] = status
        if allowed_scopes is not UNSET:
            field_dict["allowedScopes"] = allowed_scopes
        if denied_scopes is not UNSET:
            field_dict["deniedScopes"] = denied_scopes

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_result_representation import PolicyResultRepresentation
        d = dict(src_dict)
        _resource = d.pop("resource", UNSET)
        resource: Union[Unset, ResourceRepresentation]
        if isinstance(_resource,  Unset):
            resource = UNSET
        else:
            resource = ResourceRepresentation.from_dict(_resource)




        scopes = []
        _scopes = d.pop("scopes", UNSET)
        for scopes_item_data in (_scopes or []):
            scopes_item = ScopeRepresentation.from_dict(scopes_item_data)



            scopes.append(scopes_item)


        policies = []
        _policies = d.pop("policies", UNSET)
        for policies_item_data in (_policies or []):
            policies_item = PolicyResultRepresentation.from_dict(policies_item_data)



            policies.append(policies_item)


        _status = d.pop("status", UNSET)
        status: Union[Unset, DecisionEffect]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = DecisionEffect(_status)




        allowed_scopes = []
        _allowed_scopes = d.pop("allowedScopes", UNSET)
        for allowed_scopes_item_data in (_allowed_scopes or []):
            allowed_scopes_item = ScopeRepresentation.from_dict(allowed_scopes_item_data)



            allowed_scopes.append(allowed_scopes_item)


        denied_scopes = []
        _denied_scopes = d.pop("deniedScopes", UNSET)
        for denied_scopes_item_data in (_denied_scopes or []):
            denied_scopes_item = ScopeRepresentation.from_dict(denied_scopes_item_data)



            denied_scopes.append(denied_scopes_item)


        evaluation_result_representation = cls(
            resource=resource,
            scopes=scopes,
            policies=policies,
            status=status,
            allowed_scopes=allowed_scopes,
            denied_scopes=denied_scopes,
        )


        evaluation_result_representation.additional_properties = d
        return evaluation_result_representation

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
