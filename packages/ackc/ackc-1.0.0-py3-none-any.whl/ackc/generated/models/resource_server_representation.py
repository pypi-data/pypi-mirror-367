from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.decision_strategy import DecisionStrategy
from ..models.policy_enforcement_mode import PolicyEnforcementMode
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.scope_representation import ScopeRepresentation
  from ..models.resource_representation import ResourceRepresentation
  from ..models.policy_representation import PolicyRepresentation
  from ..models.authorization_schema import AuthorizationSchema





T = TypeVar("T", bound="ResourceServerRepresentation")



@_attrs_define
class ResourceServerRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            client_id (Union[Unset, str]):
            name (Union[Unset, str]):
            allow_remote_resource_management (Union[Unset, bool]):
            policy_enforcement_mode (Union[Unset, PolicyEnforcementMode]):
            resources (Union[Unset, list['ResourceRepresentation']]):
            policies (Union[Unset, list['PolicyRepresentation']]):
            scopes (Union[Unset, list['ScopeRepresentation']]):
            decision_strategy (Union[Unset, DecisionStrategy]):
            authorization_schema (Union[Unset, AuthorizationSchema]):
     """

    id: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    allow_remote_resource_management: Union[Unset, bool] = UNSET
    policy_enforcement_mode: Union[Unset, PolicyEnforcementMode] = UNSET
    resources: Union[Unset, list['ResourceRepresentation']] = UNSET
    policies: Union[Unset, list['PolicyRepresentation']] = UNSET
    scopes: Union[Unset, list['ScopeRepresentation']] = UNSET
    decision_strategy: Union[Unset, DecisionStrategy] = UNSET
    authorization_schema: Union[Unset, 'AuthorizationSchema'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_representation import PolicyRepresentation
        from ..models.authorization_schema import AuthorizationSchema
        id = self.id

        client_id = self.client_id

        name = self.name

        allow_remote_resource_management = self.allow_remote_resource_management

        policy_enforcement_mode: Union[Unset, str] = UNSET
        if not isinstance(self.policy_enforcement_mode, Unset):
            policy_enforcement_mode = self.policy_enforcement_mode.value


        resources: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = []
            for resources_item_data in self.resources:
                resources_item = resources_item_data.to_dict()
                resources.append(resources_item)



        policies: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = []
            for policies_item_data in self.policies:
                policies_item = policies_item_data.to_dict()
                policies.append(policies_item)



        scopes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = []
            for scopes_item_data in self.scopes:
                scopes_item = scopes_item_data.to_dict()
                scopes.append(scopes_item)



        decision_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.decision_strategy, Unset):
            decision_strategy = self.decision_strategy.value


        authorization_schema: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authorization_schema, Unset):
            authorization_schema = self.authorization_schema.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if name is not UNSET:
            field_dict["name"] = name
        if allow_remote_resource_management is not UNSET:
            field_dict["allowRemoteResourceManagement"] = allow_remote_resource_management
        if policy_enforcement_mode is not UNSET:
            field_dict["policyEnforcementMode"] = policy_enforcement_mode
        if resources is not UNSET:
            field_dict["resources"] = resources
        if policies is not UNSET:
            field_dict["policies"] = policies
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if decision_strategy is not UNSET:
            field_dict["decisionStrategy"] = decision_strategy
        if authorization_schema is not UNSET:
            field_dict["authorizationSchema"] = authorization_schema

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_representation import PolicyRepresentation
        from ..models.authorization_schema import AuthorizationSchema
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        client_id = d.pop("clientId", UNSET)

        name = d.pop("name", UNSET)

        allow_remote_resource_management = d.pop("allowRemoteResourceManagement", UNSET)

        _policy_enforcement_mode = d.pop("policyEnforcementMode", UNSET)
        policy_enforcement_mode: Union[Unset, PolicyEnforcementMode]
        if isinstance(_policy_enforcement_mode,  Unset):
            policy_enforcement_mode = UNSET
        else:
            policy_enforcement_mode = PolicyEnforcementMode(_policy_enforcement_mode)




        resources = []
        _resources = d.pop("resources", UNSET)
        for resources_item_data in (_resources or []):
            resources_item = ResourceRepresentation.from_dict(resources_item_data)



            resources.append(resources_item)


        policies = []
        _policies = d.pop("policies", UNSET)
        for policies_item_data in (_policies or []):
            policies_item = PolicyRepresentation.from_dict(policies_item_data)



            policies.append(policies_item)


        scopes = []
        _scopes = d.pop("scopes", UNSET)
        for scopes_item_data in (_scopes or []):
            scopes_item = ScopeRepresentation.from_dict(scopes_item_data)



            scopes.append(scopes_item)


        _decision_strategy = d.pop("decisionStrategy", UNSET)
        decision_strategy: Union[Unset, DecisionStrategy]
        if isinstance(_decision_strategy,  Unset):
            decision_strategy = UNSET
        else:
            decision_strategy = DecisionStrategy(_decision_strategy)




        _authorization_schema = d.pop("authorizationSchema", UNSET)
        authorization_schema: Union[Unset, AuthorizationSchema]
        if isinstance(_authorization_schema,  Unset):
            authorization_schema = UNSET
        else:
            authorization_schema = AuthorizationSchema.from_dict(_authorization_schema)




        resource_server_representation = cls(
            id=id,
            client_id=client_id,
            name=name,
            allow_remote_resource_management=allow_remote_resource_management,
            policy_enforcement_mode=policy_enforcement_mode,
            resources=resources,
            policies=policies,
            scopes=scopes,
            decision_strategy=decision_strategy,
            authorization_schema=authorization_schema,
        )


        resource_server_representation.additional_properties = d
        return resource_server_representation

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
