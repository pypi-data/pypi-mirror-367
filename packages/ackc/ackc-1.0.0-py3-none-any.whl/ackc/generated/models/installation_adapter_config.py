from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.installation_adapter_config_credentials import InstallationAdapterConfigCredentials
  from ..models.policy_enforcer_config import PolicyEnforcerConfig





T = TypeVar("T", bound="InstallationAdapterConfig")



@_attrs_define
class InstallationAdapterConfig:
    """ 
        Attributes:
            realm (Union[Unset, str]):
            realm_public_key (Union[Unset, str]):
            auth_server_url (Union[Unset, str]):
            ssl_required (Union[Unset, str]):
            bearer_only (Union[Unset, bool]):
            resource (Union[Unset, str]):
            public_client (Union[Unset, bool]):
            verify_token_audience (Union[Unset, bool]):
            credentials (Union[Unset, InstallationAdapterConfigCredentials]):
            use_resource_role_mappings (Union[Unset, bool]):
            confidential_port (Union[Unset, int]):
            policy_enforcer (Union[Unset, PolicyEnforcerConfig]):
     """

    realm: Union[Unset, str] = UNSET
    realm_public_key: Union[Unset, str] = UNSET
    auth_server_url: Union[Unset, str] = UNSET
    ssl_required: Union[Unset, str] = UNSET
    bearer_only: Union[Unset, bool] = UNSET
    resource: Union[Unset, str] = UNSET
    public_client: Union[Unset, bool] = UNSET
    verify_token_audience: Union[Unset, bool] = UNSET
    credentials: Union[Unset, 'InstallationAdapterConfigCredentials'] = UNSET
    use_resource_role_mappings: Union[Unset, bool] = UNSET
    confidential_port: Union[Unset, int] = UNSET
    policy_enforcer: Union[Unset, 'PolicyEnforcerConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.installation_adapter_config_credentials import InstallationAdapterConfigCredentials
        from ..models.policy_enforcer_config import PolicyEnforcerConfig
        realm = self.realm

        realm_public_key = self.realm_public_key

        auth_server_url = self.auth_server_url

        ssl_required = self.ssl_required

        bearer_only = self.bearer_only

        resource = self.resource

        public_client = self.public_client

        verify_token_audience = self.verify_token_audience

        credentials: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.credentials, Unset):
            credentials = self.credentials.to_dict()

        use_resource_role_mappings = self.use_resource_role_mappings

        confidential_port = self.confidential_port

        policy_enforcer: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy_enforcer, Unset):
            policy_enforcer = self.policy_enforcer.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if realm is not UNSET:
            field_dict["realm"] = realm
        if realm_public_key is not UNSET:
            field_dict["realm-public-key"] = realm_public_key
        if auth_server_url is not UNSET:
            field_dict["auth-server-url"] = auth_server_url
        if ssl_required is not UNSET:
            field_dict["ssl-required"] = ssl_required
        if bearer_only is not UNSET:
            field_dict["bearer-only"] = bearer_only
        if resource is not UNSET:
            field_dict["resource"] = resource
        if public_client is not UNSET:
            field_dict["public-client"] = public_client
        if verify_token_audience is not UNSET:
            field_dict["verify-token-audience"] = verify_token_audience
        if credentials is not UNSET:
            field_dict["credentials"] = credentials
        if use_resource_role_mappings is not UNSET:
            field_dict["use-resource-role-mappings"] = use_resource_role_mappings
        if confidential_port is not UNSET:
            field_dict["confidential-port"] = confidential_port
        if policy_enforcer is not UNSET:
            field_dict["policy-enforcer"] = policy_enforcer

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.installation_adapter_config_credentials import InstallationAdapterConfigCredentials
        from ..models.policy_enforcer_config import PolicyEnforcerConfig
        d = dict(src_dict)
        realm = d.pop("realm", UNSET)

        realm_public_key = d.pop("realm-public-key", UNSET)

        auth_server_url = d.pop("auth-server-url", UNSET)

        ssl_required = d.pop("ssl-required", UNSET)

        bearer_only = d.pop("bearer-only", UNSET)

        resource = d.pop("resource", UNSET)

        public_client = d.pop("public-client", UNSET)

        verify_token_audience = d.pop("verify-token-audience", UNSET)

        _credentials = d.pop("credentials", UNSET)
        credentials: Union[Unset, InstallationAdapterConfigCredentials]
        if isinstance(_credentials,  Unset):
            credentials = UNSET
        else:
            credentials = InstallationAdapterConfigCredentials.from_dict(_credentials)




        use_resource_role_mappings = d.pop("use-resource-role-mappings", UNSET)

        confidential_port = d.pop("confidential-port", UNSET)

        _policy_enforcer = d.pop("policy-enforcer", UNSET)
        policy_enforcer: Union[Unset, PolicyEnforcerConfig]
        if isinstance(_policy_enforcer,  Unset):
            policy_enforcer = UNSET
        else:
            policy_enforcer = PolicyEnforcerConfig.from_dict(_policy_enforcer)




        installation_adapter_config = cls(
            realm=realm,
            realm_public_key=realm_public_key,
            auth_server_url=auth_server_url,
            ssl_required=ssl_required,
            bearer_only=bearer_only,
            resource=resource,
            public_client=public_client,
            verify_token_audience=verify_token_audience,
            credentials=credentials,
            use_resource_role_mappings=use_resource_role_mappings,
            confidential_port=confidential_port,
            policy_enforcer=policy_enforcer,
        )


        installation_adapter_config.additional_properties = d
        return installation_adapter_config

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
