from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.authorization_schema_resource_types import AuthorizationSchemaResourceTypes





T = TypeVar("T", bound="AuthorizationSchema")



@_attrs_define
class AuthorizationSchema:
    """ 
        Attributes:
            resource_types (Union[Unset, AuthorizationSchemaResourceTypes]):
     """

    resource_types: Union[Unset, 'AuthorizationSchemaResourceTypes'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.authorization_schema_resource_types import AuthorizationSchemaResourceTypes
        resource_types: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.resource_types, Unset):
            resource_types = self.resource_types.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if resource_types is not UNSET:
            field_dict["resourceTypes"] = resource_types

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_schema_resource_types import AuthorizationSchemaResourceTypes
        d = dict(src_dict)
        _resource_types = d.pop("resourceTypes", UNSET)
        resource_types: Union[Unset, AuthorizationSchemaResourceTypes]
        if isinstance(_resource_types,  Unset):
            resource_types = UNSET
        else:
            resource_types = AuthorizationSchemaResourceTypes.from_dict(_resource_types)




        authorization_schema = cls(
            resource_types=resource_types,
        )


        authorization_schema.additional_properties = d
        return authorization_schema

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
