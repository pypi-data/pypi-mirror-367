from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ConfigPropertyRepresentation")



@_attrs_define
class ConfigPropertyRepresentation:
    """ 
        Attributes:
            name (Union[Unset, str]):
            label (Union[Unset, str]):
            help_text (Union[Unset, str]):
            type_ (Union[Unset, str]):
            default_value (Union[Unset, Any]):
            options (Union[Unset, list[str]]):
            secret (Union[Unset, bool]):
            required (Union[Unset, bool]):
            read_only (Union[Unset, bool]):
     """

    name: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    help_text: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    default_value: Union[Unset, Any] = UNSET
    options: Union[Unset, list[str]] = UNSET
    secret: Union[Unset, bool] = UNSET
    required: Union[Unset, bool] = UNSET
    read_only: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        label = self.label

        help_text = self.help_text

        type_ = self.type_

        default_value = self.default_value

        options: Union[Unset, list[str]] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options



        secret = self.secret

        required = self.required

        read_only = self.read_only


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if label is not UNSET:
            field_dict["label"] = label
        if help_text is not UNSET:
            field_dict["helpText"] = help_text
        if type_ is not UNSET:
            field_dict["type"] = type_
        if default_value is not UNSET:
            field_dict["defaultValue"] = default_value
        if options is not UNSET:
            field_dict["options"] = options
        if secret is not UNSET:
            field_dict["secret"] = secret
        if required is not UNSET:
            field_dict["required"] = required
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        label = d.pop("label", UNSET)

        help_text = d.pop("helpText", UNSET)

        type_ = d.pop("type", UNSET)

        default_value = d.pop("defaultValue", UNSET)

        options = cast(list[str], d.pop("options", UNSET))


        secret = d.pop("secret", UNSET)

        required = d.pop("required", UNSET)

        read_only = d.pop("readOnly", UNSET)

        config_property_representation = cls(
            name=name,
            label=label,
            help_text=help_text,
            type_=type_,
            default_value=default_value,
            options=options,
            secret=secret,
            required=required,
            read_only=read_only,
        )


        config_property_representation.additional_properties = d
        return config_property_representation

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
