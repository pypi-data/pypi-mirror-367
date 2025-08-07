from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.permission_claims import PermissionClaims





T = TypeVar("T", bound="Permission")



@_attrs_define
class Permission:
    """ 
        Attributes:
            rsid (Union[Unset, str]):
            rsname (Union[Unset, str]):
            scopes (Union[Unset, list[str]]):
            claims (Union[Unset, PermissionClaims]):
     """

    rsid: Union[Unset, str] = UNSET
    rsname: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    claims: Union[Unset, 'PermissionClaims'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.permission_claims import PermissionClaims
        rsid = self.rsid

        rsname = self.rsname

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        claims: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.claims, Unset):
            claims = self.claims.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if rsid is not UNSET:
            field_dict["rsid"] = rsid
        if rsname is not UNSET:
            field_dict["rsname"] = rsname
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if claims is not UNSET:
            field_dict["claims"] = claims

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.permission_claims import PermissionClaims
        d = dict(src_dict)
        rsid = d.pop("rsid", UNSET)

        rsname = d.pop("rsname", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _claims = d.pop("claims", UNSET)
        claims: Union[Unset, PermissionClaims]
        if isinstance(_claims,  Unset):
            claims = UNSET
        else:
            claims = PermissionClaims.from_dict(_claims)




        permission = cls(
            rsid=rsid,
            rsname=rsname,
            scopes=scopes,
            claims=claims,
        )


        permission.additional_properties = d
        return permission

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
