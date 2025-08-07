from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.enforcement_mode import EnforcementMode
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.policy_enforcer_config_claim_information_point import PolicyEnforcerConfigClaimInformationPoint
  from ..models.user_managed_access_config import UserManagedAccessConfig
  from ..models.path_config import PathConfig
  from ..models.policy_enforcer_config_credentials import PolicyEnforcerConfigCredentials
  from ..models.path_cache_config import PathCacheConfig





T = TypeVar("T", bound="PolicyEnforcerConfig")



@_attrs_define
class PolicyEnforcerConfig:
    """ 
        Attributes:
            enforcement_mode (Union[Unset, EnforcementMode]):
            paths (Union[Unset, list['PathConfig']]):
            path_cache (Union[Unset, PathCacheConfig]):
            lazy_load_paths (Union[Unset, bool]):
            on_deny_redirect_to (Union[Unset, str]):
            user_managed_access (Union[Unset, UserManagedAccessConfig]):
            claim_information_point (Union[Unset, PolicyEnforcerConfigClaimInformationPoint]):
            http_method_as_scope (Union[Unset, bool]):
            realm (Union[Unset, str]):
            auth_server_url (Union[Unset, str]):
            credentials (Union[Unset, PolicyEnforcerConfigCredentials]):
            resource (Union[Unset, str]):
     """

    enforcement_mode: Union[Unset, EnforcementMode] = UNSET
    paths: Union[Unset, list['PathConfig']] = UNSET
    path_cache: Union[Unset, 'PathCacheConfig'] = UNSET
    lazy_load_paths: Union[Unset, bool] = UNSET
    on_deny_redirect_to: Union[Unset, str] = UNSET
    user_managed_access: Union[Unset, 'UserManagedAccessConfig'] = UNSET
    claim_information_point: Union[Unset, 'PolicyEnforcerConfigClaimInformationPoint'] = UNSET
    http_method_as_scope: Union[Unset, bool] = UNSET
    realm: Union[Unset, str] = UNSET
    auth_server_url: Union[Unset, str] = UNSET
    credentials: Union[Unset, 'PolicyEnforcerConfigCredentials'] = UNSET
    resource: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.policy_enforcer_config_claim_information_point import PolicyEnforcerConfigClaimInformationPoint
        from ..models.user_managed_access_config import UserManagedAccessConfig
        from ..models.path_config import PathConfig
        from ..models.policy_enforcer_config_credentials import PolicyEnforcerConfigCredentials
        from ..models.path_cache_config import PathCacheConfig
        enforcement_mode: Union[Unset, str] = UNSET
        if not isinstance(self.enforcement_mode, Unset):
            enforcement_mode = self.enforcement_mode.value


        paths: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.paths, Unset):
            paths = []
            for paths_item_data in self.paths:
                paths_item = paths_item_data.to_dict()
                paths.append(paths_item)



        path_cache: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.path_cache, Unset):
            path_cache = self.path_cache.to_dict()

        lazy_load_paths = self.lazy_load_paths

        on_deny_redirect_to = self.on_deny_redirect_to

        user_managed_access: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user_managed_access, Unset):
            user_managed_access = self.user_managed_access.to_dict()

        claim_information_point: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.claim_information_point, Unset):
            claim_information_point = self.claim_information_point.to_dict()

        http_method_as_scope = self.http_method_as_scope

        realm = self.realm

        auth_server_url = self.auth_server_url

        credentials: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.credentials, Unset):
            credentials = self.credentials.to_dict()

        resource = self.resource


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if enforcement_mode is not UNSET:
            field_dict["enforcement-mode"] = enforcement_mode
        if paths is not UNSET:
            field_dict["paths"] = paths
        if path_cache is not UNSET:
            field_dict["path-cache"] = path_cache
        if lazy_load_paths is not UNSET:
            field_dict["lazy-load-paths"] = lazy_load_paths
        if on_deny_redirect_to is not UNSET:
            field_dict["on-deny-redirect-to"] = on_deny_redirect_to
        if user_managed_access is not UNSET:
            field_dict["user-managed-access"] = user_managed_access
        if claim_information_point is not UNSET:
            field_dict["claim-information-point"] = claim_information_point
        if http_method_as_scope is not UNSET:
            field_dict["http-method-as-scope"] = http_method_as_scope
        if realm is not UNSET:
            field_dict["realm"] = realm
        if auth_server_url is not UNSET:
            field_dict["auth-server-url"] = auth_server_url
        if credentials is not UNSET:
            field_dict["credentials"] = credentials
        if resource is not UNSET:
            field_dict["resource"] = resource

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_enforcer_config_claim_information_point import PolicyEnforcerConfigClaimInformationPoint
        from ..models.user_managed_access_config import UserManagedAccessConfig
        from ..models.path_config import PathConfig
        from ..models.policy_enforcer_config_credentials import PolicyEnforcerConfigCredentials
        from ..models.path_cache_config import PathCacheConfig
        d = dict(src_dict)
        _enforcement_mode = d.pop("enforcement-mode", UNSET)
        enforcement_mode: Union[Unset, EnforcementMode]
        if isinstance(_enforcement_mode,  Unset):
            enforcement_mode = UNSET
        else:
            enforcement_mode = EnforcementMode(_enforcement_mode)




        paths = []
        _paths = d.pop("paths", UNSET)
        for paths_item_data in (_paths or []):
            paths_item = PathConfig.from_dict(paths_item_data)



            paths.append(paths_item)


        _path_cache = d.pop("path-cache", UNSET)
        path_cache: Union[Unset, PathCacheConfig]
        if isinstance(_path_cache,  Unset):
            path_cache = UNSET
        else:
            path_cache = PathCacheConfig.from_dict(_path_cache)




        lazy_load_paths = d.pop("lazy-load-paths", UNSET)

        on_deny_redirect_to = d.pop("on-deny-redirect-to", UNSET)

        _user_managed_access = d.pop("user-managed-access", UNSET)
        user_managed_access: Union[Unset, UserManagedAccessConfig]
        if isinstance(_user_managed_access,  Unset):
            user_managed_access = UNSET
        else:
            user_managed_access = UserManagedAccessConfig.from_dict(_user_managed_access)




        _claim_information_point = d.pop("claim-information-point", UNSET)
        claim_information_point: Union[Unset, PolicyEnforcerConfigClaimInformationPoint]
        if isinstance(_claim_information_point,  Unset):
            claim_information_point = UNSET
        else:
            claim_information_point = PolicyEnforcerConfigClaimInformationPoint.from_dict(_claim_information_point)




        http_method_as_scope = d.pop("http-method-as-scope", UNSET)

        realm = d.pop("realm", UNSET)

        auth_server_url = d.pop("auth-server-url", UNSET)

        _credentials = d.pop("credentials", UNSET)
        credentials: Union[Unset, PolicyEnforcerConfigCredentials]
        if isinstance(_credentials,  Unset):
            credentials = UNSET
        else:
            credentials = PolicyEnforcerConfigCredentials.from_dict(_credentials)




        resource = d.pop("resource", UNSET)

        policy_enforcer_config = cls(
            enforcement_mode=enforcement_mode,
            paths=paths,
            path_cache=path_cache,
            lazy_load_paths=lazy_load_paths,
            on_deny_redirect_to=on_deny_redirect_to,
            user_managed_access=user_managed_access,
            claim_information_point=claim_information_point,
            http_method_as_scope=http_method_as_scope,
            realm=realm,
            auth_server_url=auth_server_url,
            credentials=credentials,
            resource=resource,
        )


        policy_enforcer_config.additional_properties = d
        return policy_enforcer_config

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
