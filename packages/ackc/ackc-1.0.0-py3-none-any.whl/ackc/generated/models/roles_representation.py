from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.role_representation import RoleRepresentation
  from ..models.roles_representation_client import RolesRepresentationClient
  from ..models.roles_representation_application import RolesRepresentationApplication





T = TypeVar("T", bound="RolesRepresentation")



@_attrs_define
class RolesRepresentation:
    """ 
        Attributes:
            realm (Union[Unset, list['RoleRepresentation']]):
            client (Union[Unset, RolesRepresentationClient]):
            application (Union[Unset, RolesRepresentationApplication]):
     """

    realm: Union[Unset, list['RoleRepresentation']] = UNSET
    client: Union[Unset, 'RolesRepresentationClient'] = UNSET
    application: Union[Unset, 'RolesRepresentationApplication'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.role_representation import RoleRepresentation
        from ..models.roles_representation_client import RolesRepresentationClient
        from ..models.roles_representation_application import RolesRepresentationApplication
        realm: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.realm, Unset):
            realm = []
            for realm_item_data in self.realm:
                realm_item = realm_item_data.to_dict()
                realm.append(realm_item)



        client: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client, Unset):
            client = self.client.to_dict()

        application: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.application, Unset):
            application = self.application.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if realm is not UNSET:
            field_dict["realm"] = realm
        if client is not UNSET:
            field_dict["client"] = client
        if application is not UNSET:
            field_dict["application"] = application

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.role_representation import RoleRepresentation
        from ..models.roles_representation_client import RolesRepresentationClient
        from ..models.roles_representation_application import RolesRepresentationApplication
        d = dict(src_dict)
        realm = []
        _realm = d.pop("realm", UNSET)
        for realm_item_data in (_realm or []):
            realm_item = RoleRepresentation.from_dict(realm_item_data)



            realm.append(realm_item)


        _client = d.pop("client", UNSET)
        client: Union[Unset, RolesRepresentationClient]
        if isinstance(_client,  Unset):
            client = UNSET
        else:
            client = RolesRepresentationClient.from_dict(_client)




        _application = d.pop("application", UNSET)
        application: Union[Unset, RolesRepresentationApplication]
        if isinstance(_application,  Unset):
            application = UNSET
        else:
            application = RolesRepresentationApplication.from_dict(_application)




        roles_representation = cls(
            realm=realm,
            client=client,
            application=application,
        )


        roles_representation.additional_properties = d
        return roles_representation

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
