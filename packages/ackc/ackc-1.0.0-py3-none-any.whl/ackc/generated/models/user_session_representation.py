from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_session_representation_clients import UserSessionRepresentationClients





T = TypeVar("T", bound="UserSessionRepresentation")



@_attrs_define
class UserSessionRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            username (Union[Unset, str]):
            user_id (Union[Unset, str]):
            ip_address (Union[Unset, str]):
            start (Union[Unset, int]):
            last_access (Union[Unset, int]):
            remember_me (Union[Unset, bool]):
            clients (Union[Unset, UserSessionRepresentationClients]):
            transient_user (Union[Unset, bool]):
     """

    id: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    ip_address: Union[Unset, str] = UNSET
    start: Union[Unset, int] = UNSET
    last_access: Union[Unset, int] = UNSET
    remember_me: Union[Unset, bool] = UNSET
    clients: Union[Unset, 'UserSessionRepresentationClients'] = UNSET
    transient_user: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_session_representation_clients import UserSessionRepresentationClients
        id = self.id

        username = self.username

        user_id = self.user_id

        ip_address = self.ip_address

        start = self.start

        last_access = self.last_access

        remember_me = self.remember_me

        clients: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.clients, Unset):
            clients = self.clients.to_dict()

        transient_user = self.transient_user


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if username is not UNSET:
            field_dict["username"] = username
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if ip_address is not UNSET:
            field_dict["ipAddress"] = ip_address
        if start is not UNSET:
            field_dict["start"] = start
        if last_access is not UNSET:
            field_dict["lastAccess"] = last_access
        if remember_me is not UNSET:
            field_dict["rememberMe"] = remember_me
        if clients is not UNSET:
            field_dict["clients"] = clients
        if transient_user is not UNSET:
            field_dict["transientUser"] = transient_user

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_session_representation_clients import UserSessionRepresentationClients
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        username = d.pop("username", UNSET)

        user_id = d.pop("userId", UNSET)

        ip_address = d.pop("ipAddress", UNSET)

        start = d.pop("start", UNSET)

        last_access = d.pop("lastAccess", UNSET)

        remember_me = d.pop("rememberMe", UNSET)

        _clients = d.pop("clients", UNSET)
        clients: Union[Unset, UserSessionRepresentationClients]
        if isinstance(_clients,  Unset):
            clients = UNSET
        else:
            clients = UserSessionRepresentationClients.from_dict(_clients)




        transient_user = d.pop("transientUser", UNSET)

        user_session_representation = cls(
            id=id,
            username=username,
            user_id=user_id,
            ip_address=ip_address,
            start=start,
            last_access=last_access,
            remember_me=remember_me,
            clients=clients,
            transient_user=transient_user,
        )


        user_session_representation.additional_properties = d
        return user_session_representation

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
