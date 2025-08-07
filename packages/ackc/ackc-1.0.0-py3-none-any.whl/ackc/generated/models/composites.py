from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.composites_client import CompositesClient
  from ..models.composites_application import CompositesApplication





T = TypeVar("T", bound="Composites")



@_attrs_define
class Composites:
    """ 
        Attributes:
            realm (Union[Unset, list[str]]):
            client (Union[Unset, CompositesClient]):
            application (Union[Unset, CompositesApplication]):
     """

    realm: Union[Unset, list[str]] = UNSET
    client: Union[Unset, 'CompositesClient'] = UNSET
    application: Union[Unset, 'CompositesApplication'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.composites_client import CompositesClient
        from ..models.composites_application import CompositesApplication
        realm: Union[Unset, list[str]] = UNSET
        if not isinstance(self.realm, Unset):
            realm = self.realm



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
        from ..models.composites_client import CompositesClient
        from ..models.composites_application import CompositesApplication
        d = dict(src_dict)
        realm = cast(list[str], d.pop("realm", UNSET))


        _client = d.pop("client", UNSET)
        client: Union[Unset, CompositesClient]
        if isinstance(_client,  Unset):
            client = UNSET
        else:
            client = CompositesClient.from_dict(_client)




        _application = d.pop("application", UNSET)
        application: Union[Unset, CompositesApplication]
        if isinstance(_application,  Unset):
            application = UNSET
        else:
            application = CompositesApplication.from_dict(_application)




        composites = cls(
            realm=realm,
            client=client,
            application=application,
        )


        composites.additional_properties = d
        return composites

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
