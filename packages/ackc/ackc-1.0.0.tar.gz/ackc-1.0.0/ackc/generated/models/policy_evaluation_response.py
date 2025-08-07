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
  from ..models.access_token import AccessToken
  from ..models.evaluation_result_representation import EvaluationResultRepresentation





T = TypeVar("T", bound="PolicyEvaluationResponse")



@_attrs_define
class PolicyEvaluationResponse:
    """ 
        Attributes:
            results (Union[Unset, list['EvaluationResultRepresentation']]):
            entitlements (Union[Unset, bool]):
            status (Union[Unset, DecisionEffect]):
            rpt (Union[Unset, AccessToken]):
     """

    results: Union[Unset, list['EvaluationResultRepresentation']] = UNSET
    entitlements: Union[Unset, bool] = UNSET
    status: Union[Unset, DecisionEffect] = UNSET
    rpt: Union[Unset, 'AccessToken'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.access_token import AccessToken
        from ..models.evaluation_result_representation import EvaluationResultRepresentation
        results: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)



        entitlements = self.entitlements

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        rpt: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.rpt, Unset):
            rpt = self.rpt.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if results is not UNSET:
            field_dict["results"] = results
        if entitlements is not UNSET:
            field_dict["entitlements"] = entitlements
        if status is not UNSET:
            field_dict["status"] = status
        if rpt is not UNSET:
            field_dict["rpt"] = rpt

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_token import AccessToken
        from ..models.evaluation_result_representation import EvaluationResultRepresentation
        d = dict(src_dict)
        results = []
        _results = d.pop("results", UNSET)
        for results_item_data in (_results or []):
            results_item = EvaluationResultRepresentation.from_dict(results_item_data)



            results.append(results_item)


        entitlements = d.pop("entitlements", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, DecisionEffect]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = DecisionEffect(_status)




        _rpt = d.pop("rpt", UNSET)
        rpt: Union[Unset, AccessToken]
        if isinstance(_rpt,  Unset):
            rpt = UNSET
        else:
            rpt = AccessToken.from_dict(_rpt)




        policy_evaluation_response = cls(
            results=results,
            entitlements=entitlements,
            status=status,
            rpt=rpt,
        )


        policy_evaluation_response.additional_properties = d
        return policy_evaluation_response

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
