from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.policy_evaluation_request_context_additional_property import PolicyEvaluationRequestContextAdditionalProperty





T = TypeVar("T", bound="PolicyEvaluationRequestContext")



@_attrs_define
class PolicyEvaluationRequestContext:
    """ 
     """

    additional_properties: dict[str, 'PolicyEvaluationRequestContextAdditionalProperty'] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.policy_evaluation_request_context_additional_property import PolicyEvaluationRequestContextAdditionalProperty
        
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()


        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_evaluation_request_context_additional_property import PolicyEvaluationRequestContextAdditionalProperty
        d = dict(src_dict)
        policy_evaluation_request_context = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = PolicyEvaluationRequestContextAdditionalProperty.from_dict(prop_dict)



            additional_properties[prop_name] = additional_property

        policy_evaluation_request_context.additional_properties = additional_properties
        return policy_evaluation_request_context

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> 'PolicyEvaluationRequestContextAdditionalProperty':
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: 'PolicyEvaluationRequestContextAdditionalProperty') -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
