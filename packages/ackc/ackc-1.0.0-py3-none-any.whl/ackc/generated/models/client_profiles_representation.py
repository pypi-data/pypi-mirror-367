from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.client_profile_representation import ClientProfileRepresentation





T = TypeVar("T", bound="ClientProfilesRepresentation")



@_attrs_define
class ClientProfilesRepresentation:
    """ 
        Attributes:
            profiles (Union[Unset, list['ClientProfileRepresentation']]):
            global_profiles (Union[Unset, list['ClientProfileRepresentation']]):
     """

    profiles: Union[Unset, list['ClientProfileRepresentation']] = UNSET
    global_profiles: Union[Unset, list['ClientProfileRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.client_profile_representation import ClientProfileRepresentation
        profiles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.profiles, Unset):
            profiles = []
            for profiles_item_data in self.profiles:
                profiles_item = profiles_item_data.to_dict()
                profiles.append(profiles_item)



        global_profiles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.global_profiles, Unset):
            global_profiles = []
            for global_profiles_item_data in self.global_profiles:
                global_profiles_item = global_profiles_item_data.to_dict()
                global_profiles.append(global_profiles_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if profiles is not UNSET:
            field_dict["profiles"] = profiles
        if global_profiles is not UNSET:
            field_dict["globalProfiles"] = global_profiles

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.client_profile_representation import ClientProfileRepresentation
        d = dict(src_dict)
        profiles = []
        _profiles = d.pop("profiles", UNSET)
        for profiles_item_data in (_profiles or []):
            profiles_item = ClientProfileRepresentation.from_dict(profiles_item_data)



            profiles.append(profiles_item)


        global_profiles = []
        _global_profiles = d.pop("globalProfiles", UNSET)
        for global_profiles_item_data in (_global_profiles or []):
            global_profiles_item = ClientProfileRepresentation.from_dict(global_profiles_item_data)



            global_profiles.append(global_profiles_item)


        client_profiles_representation = cls(
            profiles=profiles,
            global_profiles=global_profiles,
        )


        client_profiles_representation.additional_properties = d
        return client_profiles_representation

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
