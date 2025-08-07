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
  from ..models.policy_evaluation_request_context import PolicyEvaluationRequestContext





T = TypeVar("T", bound="PolicyEvaluationRequest")



@_attrs_define
class PolicyEvaluationRequest:
    """ 
        Attributes:
            context (Union[Unset, PolicyEvaluationRequestContext]):
            resources (Union[Unset, list['ResourceRepresentation']]):
            resource_type (Union[Unset, str]):
            client_id (Union[Unset, str]):
            user_id (Union[Unset, str]):
            role_ids (Union[Unset, list[str]]):
            entitlements (Union[Unset, bool]):
     """

    context: Union[Unset, 'PolicyEvaluationRequestContext'] = UNSET
    resources: Union[Unset, list['ResourceRepresentation']] = UNSET
    resource_type: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    role_ids: Union[Unset, list[str]] = UNSET
    entitlements: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_evaluation_request_context import PolicyEvaluationRequestContext
        context: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        resources: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = []
            for resources_item_data in self.resources:
                resources_item = resources_item_data.to_dict()
                resources.append(resources_item)



        resource_type = self.resource_type

        client_id = self.client_id

        user_id = self.user_id

        role_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.role_ids, Unset):
            role_ids = self.role_ids



        entitlements = self.entitlements


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if context is not UNSET:
            field_dict["context"] = context
        if resources is not UNSET:
            field_dict["resources"] = resources
        if resource_type is not UNSET:
            field_dict["resourceType"] = resource_type
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if role_ids is not UNSET:
            field_dict["roleIds"] = role_ids
        if entitlements is not UNSET:
            field_dict["entitlements"] = entitlements

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_representation import ResourceRepresentation
        from ..models.policy_evaluation_request_context import PolicyEvaluationRequestContext
        d = dict(src_dict)
        _context = d.pop("context", UNSET)
        context: Union[Unset, PolicyEvaluationRequestContext]
        if isinstance(_context,  Unset):
            context = UNSET
        else:
            context = PolicyEvaluationRequestContext.from_dict(_context)




        resources = []
        _resources = d.pop("resources", UNSET)
        for resources_item_data in (_resources or []):
            resources_item = ResourceRepresentation.from_dict(resources_item_data)



            resources.append(resources_item)


        resource_type = d.pop("resourceType", UNSET)

        client_id = d.pop("clientId", UNSET)

        user_id = d.pop("userId", UNSET)

        role_ids = cast(list[str], d.pop("roleIds", UNSET))


        entitlements = d.pop("entitlements", UNSET)

        policy_evaluation_request = cls(
            context=context,
            resources=resources,
            resource_type=resource_type,
            client_id=client_id,
            user_id=user_id,
            role_ids=role_ids,
            entitlements=entitlements,
        )


        policy_evaluation_request.additional_properties = d
        return policy_evaluation_request

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
