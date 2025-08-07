from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.identity_provider_representation_config import IdentityProviderRepresentationConfig





T = TypeVar("T", bound="IdentityProviderRepresentation")



@_attrs_define
class IdentityProviderRepresentation:
    """ 
        Attributes:
            alias (Union[Unset, str]):
            display_name (Union[Unset, str]):
            internal_id (Union[Unset, str]):
            provider_id (Union[Unset, str]):
            enabled (Union[Unset, bool]):
            update_profile_first_login_mode (Union[Unset, str]):
            trust_email (Union[Unset, bool]):
            store_token (Union[Unset, bool]):
            add_read_token_role_on_create (Union[Unset, bool]):
            authenticate_by_default (Union[Unset, bool]):
            link_only (Union[Unset, bool]):
            hide_on_login (Union[Unset, bool]):
            first_broker_login_flow_alias (Union[Unset, str]):
            post_broker_login_flow_alias (Union[Unset, str]):
            organization_id (Union[Unset, str]):
            config (Union[Unset, IdentityProviderRepresentationConfig]):
            update_profile_first_login (Union[Unset, bool]):
     """

    alias: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    internal_id: Union[Unset, str] = UNSET
    provider_id: Union[Unset, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    update_profile_first_login_mode: Union[Unset, str] = UNSET
    trust_email: Union[Unset, bool] = UNSET
    store_token: Union[Unset, bool] = UNSET
    add_read_token_role_on_create: Union[Unset, bool] = UNSET
    authenticate_by_default: Union[Unset, bool] = UNSET
    link_only: Union[Unset, bool] = UNSET
    hide_on_login: Union[Unset, bool] = UNSET
    first_broker_login_flow_alias: Union[Unset, str] = UNSET
    post_broker_login_flow_alias: Union[Unset, str] = UNSET
    organization_id: Union[Unset, str] = UNSET
    config: Union[Unset, 'IdentityProviderRepresentationConfig'] = UNSET
    update_profile_first_login: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.identity_provider_representation_config import IdentityProviderRepresentationConfig
        alias = self.alias

        display_name = self.display_name

        internal_id = self.internal_id

        provider_id = self.provider_id

        enabled = self.enabled

        update_profile_first_login_mode = self.update_profile_first_login_mode

        trust_email = self.trust_email

        store_token = self.store_token

        add_read_token_role_on_create = self.add_read_token_role_on_create

        authenticate_by_default = self.authenticate_by_default

        link_only = self.link_only

        hide_on_login = self.hide_on_login

        first_broker_login_flow_alias = self.first_broker_login_flow_alias

        post_broker_login_flow_alias = self.post_broker_login_flow_alias

        organization_id = self.organization_id

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        update_profile_first_login = self.update_profile_first_login


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if alias is not UNSET:
            field_dict["alias"] = alias
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if internal_id is not UNSET:
            field_dict["internalId"] = internal_id
        if provider_id is not UNSET:
            field_dict["providerId"] = provider_id
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if update_profile_first_login_mode is not UNSET:
            field_dict["updateProfileFirstLoginMode"] = update_profile_first_login_mode
        if trust_email is not UNSET:
            field_dict["trustEmail"] = trust_email
        if store_token is not UNSET:
            field_dict["storeToken"] = store_token
        if add_read_token_role_on_create is not UNSET:
            field_dict["addReadTokenRoleOnCreate"] = add_read_token_role_on_create
        if authenticate_by_default is not UNSET:
            field_dict["authenticateByDefault"] = authenticate_by_default
        if link_only is not UNSET:
            field_dict["linkOnly"] = link_only
        if hide_on_login is not UNSET:
            field_dict["hideOnLogin"] = hide_on_login
        if first_broker_login_flow_alias is not UNSET:
            field_dict["firstBrokerLoginFlowAlias"] = first_broker_login_flow_alias
        if post_broker_login_flow_alias is not UNSET:
            field_dict["postBrokerLoginFlowAlias"] = post_broker_login_flow_alias
        if organization_id is not UNSET:
            field_dict["organizationId"] = organization_id
        if config is not UNSET:
            field_dict["config"] = config
        if update_profile_first_login is not UNSET:
            field_dict["updateProfileFirstLogin"] = update_profile_first_login

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identity_provider_representation_config import IdentityProviderRepresentationConfig
        d = dict(src_dict)
        alias = d.pop("alias", UNSET)

        display_name = d.pop("displayName", UNSET)

        internal_id = d.pop("internalId", UNSET)

        provider_id = d.pop("providerId", UNSET)

        enabled = d.pop("enabled", UNSET)

        update_profile_first_login_mode = d.pop("updateProfileFirstLoginMode", UNSET)

        trust_email = d.pop("trustEmail", UNSET)

        store_token = d.pop("storeToken", UNSET)

        add_read_token_role_on_create = d.pop("addReadTokenRoleOnCreate", UNSET)

        authenticate_by_default = d.pop("authenticateByDefault", UNSET)

        link_only = d.pop("linkOnly", UNSET)

        hide_on_login = d.pop("hideOnLogin", UNSET)

        first_broker_login_flow_alias = d.pop("firstBrokerLoginFlowAlias", UNSET)

        post_broker_login_flow_alias = d.pop("postBrokerLoginFlowAlias", UNSET)

        organization_id = d.pop("organizationId", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, IdentityProviderRepresentationConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = IdentityProviderRepresentationConfig.from_dict(_config)




        update_profile_first_login = d.pop("updateProfileFirstLogin", UNSET)

        identity_provider_representation = cls(
            alias=alias,
            display_name=display_name,
            internal_id=internal_id,
            provider_id=provider_id,
            enabled=enabled,
            update_profile_first_login_mode=update_profile_first_login_mode,
            trust_email=trust_email,
            store_token=store_token,
            add_read_token_role_on_create=add_read_token_role_on_create,
            authenticate_by_default=authenticate_by_default,
            link_only=link_only,
            hide_on_login=hide_on_login,
            first_broker_login_flow_alias=first_broker_login_flow_alias,
            post_broker_login_flow_alias=post_broker_login_flow_alias,
            organization_id=organization_id,
            config=config,
            update_profile_first_login=update_profile_first_login,
        )


        identity_provider_representation.additional_properties = d
        return identity_provider_representation

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
