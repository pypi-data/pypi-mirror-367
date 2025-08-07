from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.group_representation_attributes import GroupRepresentationAttributes
  from ..models.group_representation_client_roles import GroupRepresentationClientRoles
  from ..models.group_representation_access import GroupRepresentationAccess





T = TypeVar("T", bound="GroupRepresentation")



@_attrs_define
class GroupRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            path (Union[Unset, str]):
            parent_id (Union[Unset, str]):
            sub_group_count (Union[Unset, int]):
            sub_groups (Union[Unset, list['GroupRepresentation']]):
            attributes (Union[Unset, GroupRepresentationAttributes]):
            realm_roles (Union[Unset, list[str]]):
            client_roles (Union[Unset, GroupRepresentationClientRoles]):
            access (Union[Unset, GroupRepresentationAccess]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    parent_id: Union[Unset, str] = UNSET
    sub_group_count: Union[Unset, int] = UNSET
    sub_groups: Union[Unset, list['GroupRepresentation']] = UNSET
    attributes: Union[Unset, 'GroupRepresentationAttributes'] = UNSET
    realm_roles: Union[Unset, list[str]] = UNSET
    client_roles: Union[Unset, 'GroupRepresentationClientRoles'] = UNSET
    access: Union[Unset, 'GroupRepresentationAccess'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.group_representation_attributes import GroupRepresentationAttributes
        from ..models.group_representation_client_roles import GroupRepresentationClientRoles
        from ..models.group_representation_access import GroupRepresentationAccess
        id = self.id

        name = self.name

        description = self.description

        path = self.path

        parent_id = self.parent_id

        sub_group_count = self.sub_group_count

        sub_groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sub_groups, Unset):
            sub_groups = []
            for sub_groups_item_data in self.sub_groups:
                sub_groups_item = sub_groups_item_data.to_dict()
                sub_groups.append(sub_groups_item)



        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        realm_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.realm_roles, Unset):
            realm_roles = self.realm_roles



        client_roles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client_roles, Unset):
            client_roles = self.client_roles.to_dict()

        access: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if path is not UNSET:
            field_dict["path"] = path
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if sub_group_count is not UNSET:
            field_dict["subGroupCount"] = sub_group_count
        if sub_groups is not UNSET:
            field_dict["subGroups"] = sub_groups
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if realm_roles is not UNSET:
            field_dict["realmRoles"] = realm_roles
        if client_roles is not UNSET:
            field_dict["clientRoles"] = client_roles
        if access is not UNSET:
            field_dict["access"] = access

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_representation_attributes import GroupRepresentationAttributes
        from ..models.group_representation_client_roles import GroupRepresentationClientRoles
        from ..models.group_representation_access import GroupRepresentationAccess
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        path = d.pop("path", UNSET)

        parent_id = d.pop("parentId", UNSET)

        sub_group_count = d.pop("subGroupCount", UNSET)

        sub_groups = []
        _sub_groups = d.pop("subGroups", UNSET)
        for sub_groups_item_data in (_sub_groups or []):
            sub_groups_item = GroupRepresentation.from_dict(sub_groups_item_data)



            sub_groups.append(sub_groups_item)


        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, GroupRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = GroupRepresentationAttributes.from_dict(_attributes)




        realm_roles = cast(list[str], d.pop("realmRoles", UNSET))


        _client_roles = d.pop("clientRoles", UNSET)
        client_roles: Union[Unset, GroupRepresentationClientRoles]
        if isinstance(_client_roles,  Unset):
            client_roles = UNSET
        else:
            client_roles = GroupRepresentationClientRoles.from_dict(_client_roles)




        _access = d.pop("access", UNSET)
        access: Union[Unset, GroupRepresentationAccess]
        if isinstance(_access,  Unset):
            access = UNSET
        else:
            access = GroupRepresentationAccess.from_dict(_access)




        group_representation = cls(
            id=id,
            name=name,
            description=description,
            path=path,
            parent_id=parent_id,
            sub_group_count=sub_group_count,
            sub_groups=sub_groups,
            attributes=attributes,
            realm_roles=realm_roles,
            client_roles=client_roles,
            access=access,
        )


        group_representation.additional_properties = d
        return group_representation

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
