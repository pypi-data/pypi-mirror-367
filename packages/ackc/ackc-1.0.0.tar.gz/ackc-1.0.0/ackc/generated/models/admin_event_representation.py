from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.auth_details_representation import AuthDetailsRepresentation
  from ..models.admin_event_representation_details import AdminEventRepresentationDetails





T = TypeVar("T", bound="AdminEventRepresentation")



@_attrs_define
class AdminEventRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            time (Union[Unset, int]):
            realm_id (Union[Unset, str]):
            auth_details (Union[Unset, AuthDetailsRepresentation]):
            operation_type (Union[Unset, str]):
            resource_type (Union[Unset, str]):
            resource_path (Union[Unset, str]):
            representation (Union[Unset, str]):
            error (Union[Unset, str]):
            details (Union[Unset, AdminEventRepresentationDetails]):
     """

    id: Union[Unset, str] = UNSET
    time: Union[Unset, int] = UNSET
    realm_id: Union[Unset, str] = UNSET
    auth_details: Union[Unset, 'AuthDetailsRepresentation'] = UNSET
    operation_type: Union[Unset, str] = UNSET
    resource_type: Union[Unset, str] = UNSET
    resource_path: Union[Unset, str] = UNSET
    representation: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    details: Union[Unset, 'AdminEventRepresentationDetails'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.auth_details_representation import AuthDetailsRepresentation
        from ..models.admin_event_representation_details import AdminEventRepresentationDetails
        id = self.id

        time = self.time

        realm_id = self.realm_id

        auth_details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.auth_details, Unset):
            auth_details = self.auth_details.to_dict()

        operation_type = self.operation_type

        resource_type = self.resource_type

        resource_path = self.resource_path

        representation = self.representation

        error = self.error

        details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if time is not UNSET:
            field_dict["time"] = time
        if realm_id is not UNSET:
            field_dict["realmId"] = realm_id
        if auth_details is not UNSET:
            field_dict["authDetails"] = auth_details
        if operation_type is not UNSET:
            field_dict["operationType"] = operation_type
        if resource_type is not UNSET:
            field_dict["resourceType"] = resource_type
        if resource_path is not UNSET:
            field_dict["resourcePath"] = resource_path
        if representation is not UNSET:
            field_dict["representation"] = representation
        if error is not UNSET:
            field_dict["error"] = error
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.auth_details_representation import AuthDetailsRepresentation
        from ..models.admin_event_representation_details import AdminEventRepresentationDetails
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        time = d.pop("time", UNSET)

        realm_id = d.pop("realmId", UNSET)

        _auth_details = d.pop("authDetails", UNSET)
        auth_details: Union[Unset, AuthDetailsRepresentation]
        if isinstance(_auth_details,  Unset):
            auth_details = UNSET
        else:
            auth_details = AuthDetailsRepresentation.from_dict(_auth_details)




        operation_type = d.pop("operationType", UNSET)

        resource_type = d.pop("resourceType", UNSET)

        resource_path = d.pop("resourcePath", UNSET)

        representation = d.pop("representation", UNSET)

        error = d.pop("error", UNSET)

        _details = d.pop("details", UNSET)
        details: Union[Unset, AdminEventRepresentationDetails]
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = AdminEventRepresentationDetails.from_dict(_details)




        admin_event_representation = cls(
            id=id,
            time=time,
            realm_id=realm_id,
            auth_details=auth_details,
            operation_type=operation_type,
            resource_type=resource_type,
            resource_path=resource_path,
            representation=representation,
            error=error,
            details=details,
        )


        admin_event_representation.additional_properties = d
        return admin_event_representation

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
