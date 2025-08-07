from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_policy_condition_representation_configuration import ClientPolicyConditionRepresentationConfiguration





T = TypeVar("T", bound="ClientPolicyConditionRepresentation")



@_attrs_define
class ClientPolicyConditionRepresentation:
    """ 
        Attributes:
            condition (Union[Unset, str]):
            configuration (Union[Unset, ClientPolicyConditionRepresentationConfiguration]): Configuration settings as a JSON
                object
     """

    condition: Union[Unset, str] = UNSET
    configuration: Union[Unset, 'ClientPolicyConditionRepresentationConfiguration'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_policy_condition_representation_configuration import ClientPolicyConditionRepresentationConfiguration
        condition = self.condition

        configuration: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.configuration, Unset):
            configuration = self.configuration.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if condition is not UNSET:
            field_dict["condition"] = condition
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_policy_condition_representation_configuration import ClientPolicyConditionRepresentationConfiguration
        d = dict(src_dict)
        condition = d.pop("condition", UNSET)

        _configuration = d.pop("configuration", UNSET)
        configuration: Union[Unset, ClientPolicyConditionRepresentationConfiguration]
        if isinstance(_configuration,  Unset):
            configuration = UNSET
        else:
            configuration = ClientPolicyConditionRepresentationConfiguration.from_dict(_configuration)




        client_policy_condition_representation = cls(
            condition=condition,
            configuration=configuration,
        )


        client_policy_condition_representation.additional_properties = d
        return client_policy_condition_representation

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
