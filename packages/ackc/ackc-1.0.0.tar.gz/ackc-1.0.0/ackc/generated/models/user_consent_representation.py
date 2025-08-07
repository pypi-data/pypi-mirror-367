from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="UserConsentRepresentation")



@_attrs_define
class UserConsentRepresentation:
    """ 
        Attributes:
            client_id (Union[Unset, str]):
            granted_client_scopes (Union[Unset, list[str]]):
            created_date (Union[Unset, int]):
            last_updated_date (Union[Unset, int]):
            granted_realm_roles (Union[Unset, list[str]]):
     """

    client_id: Union[Unset, str] = UNSET
    granted_client_scopes: Union[Unset, list[str]] = UNSET
    created_date: Union[Unset, int] = UNSET
    last_updated_date: Union[Unset, int] = UNSET
    granted_realm_roles: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        granted_client_scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.granted_client_scopes, Unset):
            granted_client_scopes = self.granted_client_scopes



        created_date = self.created_date

        last_updated_date = self.last_updated_date

        granted_realm_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.granted_realm_roles, Unset):
            granted_realm_roles = self.granted_realm_roles




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if granted_client_scopes is not UNSET:
            field_dict["grantedClientScopes"] = granted_client_scopes
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if last_updated_date is not UNSET:
            field_dict["lastUpdatedDate"] = last_updated_date
        if granted_realm_roles is not UNSET:
            field_dict["grantedRealmRoles"] = granted_realm_roles

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("clientId", UNSET)

        granted_client_scopes = cast(list[str], d.pop("grantedClientScopes", UNSET))


        created_date = d.pop("createdDate", UNSET)

        last_updated_date = d.pop("lastUpdatedDate", UNSET)

        granted_realm_roles = cast(list[str], d.pop("grantedRealmRoles", UNSET))


        user_consent_representation = cls(
            client_id=client_id,
            granted_client_scopes=granted_client_scopes,
            created_date=created_date,
            last_updated_date=last_updated_date,
            granted_realm_roles=granted_realm_roles,
        )


        user_consent_representation.additional_properties = d
        return user_consent_representation

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
