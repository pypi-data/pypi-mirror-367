from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.composites import Composites
  from ..models.role_representation_attributes import RoleRepresentationAttributes





T = TypeVar("T", bound="RoleRepresentation")



@_attrs_define
class RoleRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            scope_param_required (Union[Unset, bool]):
            composite (Union[Unset, bool]):
            composites (Union[Unset, Composites]):
            client_role (Union[Unset, bool]):
            container_id (Union[Unset, str]):
            attributes (Union[Unset, RoleRepresentationAttributes]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    scope_param_required: Union[Unset, bool] = UNSET
    composite: Union[Unset, bool] = UNSET
    composites: Union[Unset, 'Composites'] = UNSET
    client_role: Union[Unset, bool] = UNSET
    container_id: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'RoleRepresentationAttributes'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.composites import Composites
        from ..models.role_representation_attributes import RoleRepresentationAttributes
        id = self.id

        name = self.name

        description = self.description

        scope_param_required = self.scope_param_required

        composite = self.composite

        composites: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.composites, Unset):
            composites = self.composites.to_dict()

        client_role = self.client_role

        container_id = self.container_id

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()


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
        if scope_param_required is not UNSET:
            field_dict["scopeParamRequired"] = scope_param_required
        if composite is not UNSET:
            field_dict["composite"] = composite
        if composites is not UNSET:
            field_dict["composites"] = composites
        if client_role is not UNSET:
            field_dict["clientRole"] = client_role
        if container_id is not UNSET:
            field_dict["containerId"] = container_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.composites import Composites
        from ..models.role_representation_attributes import RoleRepresentationAttributes
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        scope_param_required = d.pop("scopeParamRequired", UNSET)

        composite = d.pop("composite", UNSET)

        _composites = d.pop("composites", UNSET)
        composites: Union[Unset, Composites]
        if isinstance(_composites,  Unset):
            composites = UNSET
        else:
            composites = Composites.from_dict(_composites)




        client_role = d.pop("clientRole", UNSET)

        container_id = d.pop("containerId", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, RoleRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = RoleRepresentationAttributes.from_dict(_attributes)




        role_representation = cls(
            id=id,
            name=name,
            description=description,
            scope_param_required=scope_param_required,
            composite=composite,
            composites=composites,
            client_role=client_role,
            container_id=container_id,
            attributes=attributes,
        )


        role_representation.additional_properties = d
        return role_representation

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
