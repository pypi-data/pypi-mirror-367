from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.up_attribute_permissions import UPAttributePermissions
  from ..models.up_attribute_selector import UPAttributeSelector
  from ..models.up_attribute_validations import UPAttributeValidations
  from ..models.up_attribute_required import UPAttributeRequired
  from ..models.up_attribute_annotations import UPAttributeAnnotations





T = TypeVar("T", bound="UPAttribute")



@_attrs_define
class UPAttribute:
    """ 
        Attributes:
            name (Union[Unset, str]):
            display_name (Union[Unset, str]):
            validations (Union[Unset, UPAttributeValidations]):
            annotations (Union[Unset, UPAttributeAnnotations]):
            required (Union[Unset, UPAttributeRequired]):
            permissions (Union[Unset, UPAttributePermissions]):
            selector (Union[Unset, UPAttributeSelector]):
            group (Union[Unset, str]):
            multivalued (Union[Unset, bool]):
     """

    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    validations: Union[Unset, 'UPAttributeValidations'] = UNSET
    annotations: Union[Unset, 'UPAttributeAnnotations'] = UNSET
    required: Union[Unset, 'UPAttributeRequired'] = UNSET
    permissions: Union[Unset, 'UPAttributePermissions'] = UNSET
    selector: Union[Unset, 'UPAttributeSelector'] = UNSET
    group: Union[Unset, str] = UNSET
    multivalued: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.up_attribute_permissions import UPAttributePermissions
        from ..models.up_attribute_selector import UPAttributeSelector
        from ..models.up_attribute_validations import UPAttributeValidations
        from ..models.up_attribute_required import UPAttributeRequired
        from ..models.up_attribute_annotations import UPAttributeAnnotations
        name = self.name

        display_name = self.display_name

        validations: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.validations, Unset):
            validations = self.validations.to_dict()

        annotations: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = self.annotations.to_dict()

        required: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.required, Unset):
            required = self.required.to_dict()

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        selector: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.selector, Unset):
            selector = self.selector.to_dict()

        group = self.group

        multivalued = self.multivalued


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if validations is not UNSET:
            field_dict["validations"] = validations
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if required is not UNSET:
            field_dict["required"] = required
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if selector is not UNSET:
            field_dict["selector"] = selector
        if group is not UNSET:
            field_dict["group"] = group
        if multivalued is not UNSET:
            field_dict["multivalued"] = multivalued

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.up_attribute_permissions import UPAttributePermissions
        from ..models.up_attribute_selector import UPAttributeSelector
        from ..models.up_attribute_validations import UPAttributeValidations
        from ..models.up_attribute_required import UPAttributeRequired
        from ..models.up_attribute_annotations import UPAttributeAnnotations
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        display_name = d.pop("displayName", UNSET)

        _validations = d.pop("validations", UNSET)
        validations: Union[Unset, UPAttributeValidations]
        if isinstance(_validations,  Unset):
            validations = UNSET
        else:
            validations = UPAttributeValidations.from_dict(_validations)




        _annotations = d.pop("annotations", UNSET)
        annotations: Union[Unset, UPAttributeAnnotations]
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = UPAttributeAnnotations.from_dict(_annotations)




        _required = d.pop("required", UNSET)
        required: Union[Unset, UPAttributeRequired]
        if isinstance(_required,  Unset):
            required = UNSET
        else:
            required = UPAttributeRequired.from_dict(_required)




        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, UPAttributePermissions]
        if isinstance(_permissions,  Unset):
            permissions = UNSET
        else:
            permissions = UPAttributePermissions.from_dict(_permissions)




        _selector = d.pop("selector", UNSET)
        selector: Union[Unset, UPAttributeSelector]
        if isinstance(_selector,  Unset):
            selector = UNSET
        else:
            selector = UPAttributeSelector.from_dict(_selector)




        group = d.pop("group", UNSET)

        multivalued = d.pop("multivalued", UNSET)

        up_attribute = cls(
            name=name,
            display_name=display_name,
            validations=validations,
            annotations=annotations,
            required=required,
            permissions=permissions,
            selector=selector,
            group=group,
            multivalued=multivalued,
        )


        up_attribute.additional_properties = d
        return up_attribute

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
