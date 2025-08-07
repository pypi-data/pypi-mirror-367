from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.management_permission_reference_scope_permissions import ManagementPermissionReferenceScopePermissions





T = TypeVar("T", bound="ManagementPermissionReference")



@_attrs_define
class ManagementPermissionReference:
    """ 
        Attributes:
            enabled (Union[Unset, bool]):
            resource (Union[Unset, str]):
            scope_permissions (Union[Unset, ManagementPermissionReferenceScopePermissions]):
     """

    enabled: Union[Unset, bool] = UNSET
    resource: Union[Unset, str] = UNSET
    scope_permissions: Union[Unset, 'ManagementPermissionReferenceScopePermissions'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.management_permission_reference_scope_permissions import ManagementPermissionReferenceScopePermissions
        enabled = self.enabled

        resource = self.resource

        scope_permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.scope_permissions, Unset):
            scope_permissions = self.scope_permissions.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if resource is not UNSET:
            field_dict["resource"] = resource
        if scope_permissions is not UNSET:
            field_dict["scopePermissions"] = scope_permissions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.management_permission_reference_scope_permissions import ManagementPermissionReferenceScopePermissions
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        resource = d.pop("resource", UNSET)

        _scope_permissions = d.pop("scopePermissions", UNSET)
        scope_permissions: Union[Unset, ManagementPermissionReferenceScopePermissions]
        if isinstance(_scope_permissions,  Unset):
            scope_permissions = UNSET
        else:
            scope_permissions = ManagementPermissionReferenceScopePermissions.from_dict(_scope_permissions)




        management_permission_reference = cls(
            enabled=enabled,
            resource=resource,
            scope_permissions=scope_permissions,
        )


        management_permission_reference.additional_properties = d
        return management_permission_reference

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
