from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="GlobalRequestResult")



@_attrs_define
class GlobalRequestResult:
    """ 
        Attributes:
            success_requests (Union[Unset, list[str]]):
            failed_requests (Union[Unset, list[str]]):
     """

    success_requests: Union[Unset, list[str]] = UNSET
    failed_requests: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        success_requests: Union[Unset, list[str]] = UNSET
        if not isinstance(self.success_requests, Unset):
            success_requests = self.success_requests



        failed_requests: Union[Unset, list[str]] = UNSET
        if not isinstance(self.failed_requests, Unset):
            failed_requests = self.failed_requests




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if success_requests is not UNSET:
            field_dict["successRequests"] = success_requests
        if failed_requests is not UNSET:
            field_dict["failedRequests"] = failed_requests

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success_requests = cast(list[str], d.pop("successRequests", UNSET))


        failed_requests = cast(list[str], d.pop("failedRequests", UNSET))


        global_request_result = cls(
            success_requests=success_requests,
            failed_requests=failed_requests,
        )


        global_request_result.additional_properties = d
        return global_request_result

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
