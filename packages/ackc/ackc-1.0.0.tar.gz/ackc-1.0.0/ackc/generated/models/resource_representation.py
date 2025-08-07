from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.scope_representation import ScopeRepresentation
  from ..models.resource_representation_attributes import ResourceRepresentationAttributes
  from ..models.resource_owner_representation import ResourceOwnerRepresentation





T = TypeVar("T", bound="ResourceRepresentation")



@_attrs_define
class ResourceRepresentation:
    """ 
        Attributes:
            field_id (Union[Unset, str]):
            name (Union[Unset, str]):
            uris (Union[Unset, list[str]]):
            type_ (Union[Unset, str]):
            scopes (Union[Unset, list['ScopeRepresentation']]):
            icon_uri (Union[Unset, str]):
            owner (Union[Unset, ResourceOwnerRepresentation]):
            owner_managed_access (Union[Unset, bool]):
            display_name (Union[Unset, str]):
            attributes (Union[Unset, ResourceRepresentationAttributes]):
            uri (Union[Unset, str]):
            scopes_uma (Union[Unset, list['ScopeRepresentation']]):
     """

    field_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    uris: Union[Unset, list[str]] = UNSET
    type_: Union[Unset, str] = UNSET
    scopes: Union[Unset, list['ScopeRepresentation']] = UNSET
    icon_uri: Union[Unset, str] = UNSET
    owner: Union[Unset, 'ResourceOwnerRepresentation'] = UNSET
    owner_managed_access: Union[Unset, bool] = UNSET
    display_name: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'ResourceRepresentationAttributes'] = UNSET
    uri: Union[Unset, str] = UNSET
    scopes_uma: Union[Unset, list['ScopeRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation_attributes import ResourceRepresentationAttributes
        from ..models.resource_owner_representation import ResourceOwnerRepresentation
        field_id = self.field_id

        name = self.name

        uris: Union[Unset, list[str]] = UNSET
        if not isinstance(self.uris, Unset):
            uris = self.uris



        type_ = self.type_

        scopes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = []
            for scopes_item_data in self.scopes:
                scopes_item = scopes_item_data.to_dict()
                scopes.append(scopes_item)



        icon_uri = self.icon_uri

        owner: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.owner, Unset):
            owner = self.owner.to_dict()

        owner_managed_access = self.owner_managed_access

        display_name = self.display_name

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        uri = self.uri

        scopes_uma: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.scopes_uma, Unset):
            scopes_uma = []
            for scopes_uma_item_data in self.scopes_uma:
                scopes_uma_item = scopes_uma_item_data.to_dict()
                scopes_uma.append(scopes_uma_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if name is not UNSET:
            field_dict["name"] = name
        if uris is not UNSET:
            field_dict["uris"] = uris
        if type_ is not UNSET:
            field_dict["type"] = type_
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if icon_uri is not UNSET:
            field_dict["icon_uri"] = icon_uri
        if owner is not UNSET:
            field_dict["owner"] = owner
        if owner_managed_access is not UNSET:
            field_dict["ownerManagedAccess"] = owner_managed_access
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if uri is not UNSET:
            field_dict["uri"] = uri
        if scopes_uma is not UNSET:
            field_dict["scopesUma"] = scopes_uma

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scope_representation import ScopeRepresentation
        from ..models.resource_representation_attributes import ResourceRepresentationAttributes
        from ..models.resource_owner_representation import ResourceOwnerRepresentation
        d = dict(src_dict)
        field_id = d.pop("_id", UNSET)

        name = d.pop("name", UNSET)

        uris = cast(list[str], d.pop("uris", UNSET))


        type_ = d.pop("type", UNSET)

        scopes = []
        _scopes = d.pop("scopes", UNSET)
        for scopes_item_data in (_scopes or []):
            scopes_item = ScopeRepresentation.from_dict(scopes_item_data)



            scopes.append(scopes_item)


        icon_uri = d.pop("icon_uri", UNSET)

        _owner = d.pop("owner", UNSET)
        owner: Union[Unset, ResourceOwnerRepresentation]
        if isinstance(_owner,  Unset):
            owner = UNSET
        else:
            owner = ResourceOwnerRepresentation.from_dict(_owner)




        owner_managed_access = d.pop("ownerManagedAccess", UNSET)

        display_name = d.pop("displayName", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, ResourceRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = ResourceRepresentationAttributes.from_dict(_attributes)




        uri = d.pop("uri", UNSET)

        scopes_uma = []
        _scopes_uma = d.pop("scopesUma", UNSET)
        for scopes_uma_item_data in (_scopes_uma or []):
            scopes_uma_item = ScopeRepresentation.from_dict(scopes_uma_item_data)



            scopes_uma.append(scopes_uma_item)


        resource_representation = cls(
            field_id=field_id,
            name=name,
            uris=uris,
            type_=type_,
            scopes=scopes,
            icon_uri=icon_uri,
            owner=owner,
            owner_managed_access=owner_managed_access,
            display_name=display_name,
            attributes=attributes,
            uri=uri,
            scopes_uma=scopes_uma,
        )


        resource_representation.additional_properties = d
        return resource_representation

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
