from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.decision_strategy import DecisionStrategy
from ..models.logic import Logic
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.scope_representation import ScopeRepresentation
  from ..models.resource_representation import ResourceRepresentation





T = TypeVar("T", bound="AbstractPolicyRepresentation")



@_attrs_define
class AbstractPolicyRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            type_ (Union[Unset, str]):
            policies (Union[Unset, list[str]]):
            resources (Union[Unset, list[str]]):
            scopes (Union[Unset, list[str]]):
            logic (Union[Unset, Logic]):
            decision_strategy (Union[Unset, DecisionStrategy]):
            owner (Union[Unset, str]):
            resource_type (Union[Unset, str]):
            resources_data (Union[Unset, list['ResourceRepresentation']]):
            scopes_data (Union[Unset, list['ScopeRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    policies: Union[Unset, list[str]] = UNSET
    resources: Union[Unset, list[str]] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    logic: Union[Unset, Logic] = UNSET
    decision_strategy: Union[Unset, DecisionStrategy] = UNSET
    owner: Union[Unset, str] = UNSET
    resource_type: Union[Unset, str] = UNSET
    resources_data: Union[Unset, list['ResourceRepresentation']] = UNSET
    scopes_data: Union[Unset, list['ScopeRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation import ResourceRepresentation
        id = self.id

        name = self.name

        description = self.description

        type_ = self.type_

        policies: Union[Unset, list[str]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = self.policies



        resources: Union[Unset, list[str]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = self.resources



        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        logic: Union[Unset, str] = UNSET
        if not isinstance(self.logic, Unset):
            logic = self.logic.value


        decision_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.decision_strategy, Unset):
            decision_strategy = self.decision_strategy.value


        owner = self.owner

        resource_type = self.resource_type

        resources_data: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.resources_data, Unset):
            resources_data = []
            for resources_data_item_data in self.resources_data:
                resources_data_item = resources_data_item_data.to_dict()
                resources_data.append(resources_data_item)



        scopes_data: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.scopes_data, Unset):
            scopes_data = []
            for scopes_data_item_data in self.scopes_data:
                scopes_data_item = scopes_data_item_data.to_dict()
                scopes_data.append(scopes_data_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if type_ is not UNSET:
            field_dict["type"] = type_
        if policies is not UNSET:
            field_dict["policies"] = policies
        if resources is not UNSET:
            field_dict["resources"] = resources
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if logic is not UNSET:
            field_dict["logic"] = logic
        if decision_strategy is not UNSET:
            field_dict["decisionStrategy"] = decision_strategy
        if owner is not UNSET:
            field_dict["owner"] = owner
        if resource_type is not UNSET:
            field_dict["resourceType"] = resource_type
        if resources_data is not UNSET:
            field_dict["resourcesData"] = resources_data
        if scopes_data is not UNSET:
            field_dict["scopesData"] = scopes_data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation import ResourceRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        type_ = d.pop("type", UNSET)

        policies = cast(list[str], d.pop("policies", UNSET))


        resources = cast(list[str], d.pop("resources", UNSET))


        scopes = cast(list[str], d.pop("scopes", UNSET))


        _logic = d.pop("logic", UNSET)
        logic: Union[Unset, Logic]
        if isinstance(_logic,  Unset):
            logic = UNSET
        else:
            logic = Logic(_logic)




        _decision_strategy = d.pop("decisionStrategy", UNSET)
        decision_strategy: Union[Unset, DecisionStrategy]
        if isinstance(_decision_strategy,  Unset):
            decision_strategy = UNSET
        else:
            decision_strategy = DecisionStrategy(_decision_strategy)




        owner = d.pop("owner", UNSET)

        resource_type = d.pop("resourceType", UNSET)

        resources_data = []
        _resources_data = d.pop("resourcesData", UNSET)
        for resources_data_item_data in (_resources_data or []):
            resources_data_item = ResourceRepresentation.from_dict(resources_data_item_data)



            resources_data.append(resources_data_item)


        scopes_data = []
        _scopes_data = d.pop("scopesData", UNSET)
        for scopes_data_item_data in (_scopes_data or []):
            scopes_data_item = ScopeRepresentation.from_dict(scopes_data_item_data)



            scopes_data.append(scopes_data_item)


        abstract_policy_representation = cls(
            id=id,
            name=name,
            description=description,
            type_=type_,
            policies=policies,
            resources=resources,
            scopes=scopes,
            logic=logic,
            decision_strategy=decision_strategy,
            owner=owner,
            resource_type=resource_type,
            resources_data=resources_data,
            scopes_data=scopes_data,
        )


        abstract_policy_representation.additional_properties = d
        return abstract_policy_representation

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
