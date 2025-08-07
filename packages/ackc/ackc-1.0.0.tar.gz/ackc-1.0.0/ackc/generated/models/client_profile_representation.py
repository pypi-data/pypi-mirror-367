from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_policy_executor_representation import ClientPolicyExecutorRepresentation





T = TypeVar("T", bound="ClientProfileRepresentation")



@_attrs_define
class ClientProfileRepresentation:
    """ 
        Attributes:
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            executors (Union[Unset, list['ClientPolicyExecutorRepresentation']]):
     """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    executors: Union[Unset, list['ClientPolicyExecutorRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_policy_executor_representation import ClientPolicyExecutorRepresentation
        name = self.name

        description = self.description

        executors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.executors, Unset):
            executors = []
            for executors_item_data in self.executors:
                executors_item = executors_item_data.to_dict()
                executors.append(executors_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if executors is not UNSET:
            field_dict["executors"] = executors

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_policy_executor_representation import ClientPolicyExecutorRepresentation
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        executors = []
        _executors = d.pop("executors", UNSET)
        for executors_item_data in (_executors or []):
            executors_item = ClientPolicyExecutorRepresentation.from_dict(executors_item_data)



            executors.append(executors_item)


        client_profile_representation = cls(
            name=name,
            description=description,
            executors=executors,
        )


        client_profile_representation.additional_properties = d
        return client_profile_representation

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
