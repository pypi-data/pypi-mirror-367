from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_profile_attribute_metadata_annotations import UserProfileAttributeMetadataAnnotations
  from ..models.user_profile_attribute_metadata_validators import UserProfileAttributeMetadataValidators





T = TypeVar("T", bound="UserProfileAttributeMetadata")



@_attrs_define
class UserProfileAttributeMetadata:
    """ 
        Attributes:
            name (Union[Unset, str]):
            display_name (Union[Unset, str]):
            required (Union[Unset, bool]):
            read_only (Union[Unset, bool]):
            annotations (Union[Unset, UserProfileAttributeMetadataAnnotations]):
            validators (Union[Unset, UserProfileAttributeMetadataValidators]):
            group (Union[Unset, str]):
            multivalued (Union[Unset, bool]):
     """

    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    required: Union[Unset, bool] = UNSET
    read_only: Union[Unset, bool] = UNSET
    annotations: Union[Unset, 'UserProfileAttributeMetadataAnnotations'] = UNSET
    validators: Union[Unset, 'UserProfileAttributeMetadataValidators'] = UNSET
    group: Union[Unset, str] = UNSET
    multivalued: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_profile_attribute_metadata_annotations import UserProfileAttributeMetadataAnnotations
        from ..models.user_profile_attribute_metadata_validators import UserProfileAttributeMetadataValidators
        name = self.name

        display_name = self.display_name

        required = self.required

        read_only = self.read_only

        annotations: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = self.annotations.to_dict()

        validators: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.validators, Unset):
            validators = self.validators.to_dict()

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
        if required is not UNSET:
            field_dict["required"] = required
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if validators is not UNSET:
            field_dict["validators"] = validators
        if group is not UNSET:
            field_dict["group"] = group
        if multivalued is not UNSET:
            field_dict["multivalued"] = multivalued

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_profile_attribute_metadata_annotations import UserProfileAttributeMetadataAnnotations
        from ..models.user_profile_attribute_metadata_validators import UserProfileAttributeMetadataValidators
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        display_name = d.pop("displayName", UNSET)

        required = d.pop("required", UNSET)

        read_only = d.pop("readOnly", UNSET)

        _annotations = d.pop("annotations", UNSET)
        annotations: Union[Unset, UserProfileAttributeMetadataAnnotations]
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = UserProfileAttributeMetadataAnnotations.from_dict(_annotations)




        _validators = d.pop("validators", UNSET)
        validators: Union[Unset, UserProfileAttributeMetadataValidators]
        if isinstance(_validators,  Unset):
            validators = UNSET
        else:
            validators = UserProfileAttributeMetadataValidators.from_dict(_validators)




        group = d.pop("group", UNSET)

        multivalued = d.pop("multivalued", UNSET)

        user_profile_attribute_metadata = cls(
            name=name,
            display_name=display_name,
            required=required,
            read_only=read_only,
            annotations=annotations,
            validators=validators,
            group=group,
            multivalued=multivalued,
        )


        user_profile_attribute_metadata.additional_properties = d
        return user_profile_attribute_metadata

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
