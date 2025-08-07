from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_policy_executor_representation_configuration import ClientPolicyExecutorRepresentationConfiguration





T = TypeVar("T", bound="ClientPolicyExecutorRepresentation")



@_attrs_define
class ClientPolicyExecutorRepresentation:
    """ 
        Attributes:
            executor (Union[Unset, str]):
            configuration (Union[Unset, ClientPolicyExecutorRepresentationConfiguration]): Configuration settings as a JSON
                object
     """

    executor: Union[Unset, str] = UNSET
    configuration: Union[Unset, 'ClientPolicyExecutorRepresentationConfiguration'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_policy_executor_representation_configuration import ClientPolicyExecutorRepresentationConfiguration
        executor = self.executor

        configuration: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.configuration, Unset):
            configuration = self.configuration.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if executor is not UNSET:
            field_dict["executor"] = executor
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_policy_executor_representation_configuration import ClientPolicyExecutorRepresentationConfiguration
        d = dict(src_dict)
        executor = d.pop("executor", UNSET)

        _configuration = d.pop("configuration", UNSET)
        configuration: Union[Unset, ClientPolicyExecutorRepresentationConfiguration]
        if isinstance(_configuration,  Unset):
            configuration = UNSET
        else:
            configuration = ClientPolicyExecutorRepresentationConfiguration.from_dict(_configuration)




        client_policy_executor_representation = cls(
            executor=executor,
            configuration=configuration,
        )


        client_policy_executor_representation.additional_properties = d
        return client_policy_executor_representation

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
