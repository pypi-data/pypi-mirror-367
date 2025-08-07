from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ErrorRepresentation")



@_attrs_define
class ErrorRepresentation:
    """ 
        Attributes:
            field (Union[Unset, str]):
            error_message (Union[Unset, str]):
            params (Union[Unset, list[Any]]):
            errors (Union[Unset, list['ErrorRepresentation']]):
     """

    field: Union[Unset, str] = UNSET
    error_message: Union[Unset, str] = UNSET
    params: Union[Unset, list[Any]] = UNSET
    errors: Union[Unset, list['ErrorRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        field = self.field

        error_message = self.error_message

        params: Union[Unset, list[Any]] = UNSET
        if not isinstance(self.params, Unset):
            params = self.params



        errors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if field is not UNSET:
            field_dict["field"] = field
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if params is not UNSET:
            field_dict["params"] = params
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        params = cast(list[Any], d.pop("params", UNSET))


        errors = []
        _errors = d.pop("errors", UNSET)
        for errors_item_data in (_errors or []):
            errors_item = ErrorRepresentation.from_dict(errors_item_data)



            errors.append(errors_item)


        error_representation = cls(
            field=field,
            error_message=error_message,
            params=params,
            errors=errors,
        )


        error_representation.additional_properties = d
        return error_representation

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
