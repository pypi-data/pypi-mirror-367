from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_representation_application_roles import UserRepresentationApplicationRoles
  from ..models.user_representation_client_roles import UserRepresentationClientRoles
  from ..models.user_profile_metadata import UserProfileMetadata
  from ..models.user_representation_attributes import UserRepresentationAttributes
  from ..models.federated_identity_representation import FederatedIdentityRepresentation
  from ..models.user_representation_access import UserRepresentationAccess
  from ..models.credential_representation import CredentialRepresentation
  from ..models.user_consent_representation import UserConsentRepresentation
  from ..models.social_link_representation import SocialLinkRepresentation





T = TypeVar("T", bound="UserRepresentation")



@_attrs_define
class UserRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            username (Union[Unset, str]):
            first_name (Union[Unset, str]):
            last_name (Union[Unset, str]):
            email (Union[Unset, str]):
            email_verified (Union[Unset, bool]):
            attributes (Union[Unset, UserRepresentationAttributes]):
            user_profile_metadata (Union[Unset, UserProfileMetadata]):
            enabled (Union[Unset, bool]):
            self_ (Union[Unset, str]):
            origin (Union[Unset, str]):
            created_timestamp (Union[Unset, int]):
            totp (Union[Unset, bool]):
            federation_link (Union[Unset, str]):
            service_account_client_id (Union[Unset, str]):
            credentials (Union[Unset, list['CredentialRepresentation']]):
            disableable_credential_types (Union[Unset, list[str]]):
            required_actions (Union[Unset, list[str]]):
            federated_identities (Union[Unset, list['FederatedIdentityRepresentation']]):
            realm_roles (Union[Unset, list[str]]):
            client_roles (Union[Unset, UserRepresentationClientRoles]):
            client_consents (Union[Unset, list['UserConsentRepresentation']]):
            not_before (Union[Unset, int]):
            application_roles (Union[Unset, UserRepresentationApplicationRoles]):
            social_links (Union[Unset, list['SocialLinkRepresentation']]):
            groups (Union[Unset, list[str]]):
            access (Union[Unset, UserRepresentationAccess]):
     """

    id: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    email_verified: Union[Unset, bool] = UNSET
    attributes: Union[Unset, 'UserRepresentationAttributes'] = UNSET
    user_profile_metadata: Union[Unset, 'UserProfileMetadata'] = UNSET
    enabled: Union[Unset, bool] = UNSET
    self_: Union[Unset, str] = UNSET
    origin: Union[Unset, str] = UNSET
    created_timestamp: Union[Unset, int] = UNSET
    totp: Union[Unset, bool] = UNSET
    federation_link: Union[Unset, str] = UNSET
    service_account_client_id: Union[Unset, str] = UNSET
    credentials: Union[Unset, list['CredentialRepresentation']] = UNSET
    disableable_credential_types: Union[Unset, list[str]] = UNSET
    required_actions: Union[Unset, list[str]] = UNSET
    federated_identities: Union[Unset, list['FederatedIdentityRepresentation']] = UNSET
    realm_roles: Union[Unset, list[str]] = UNSET
    client_roles: Union[Unset, 'UserRepresentationClientRoles'] = UNSET
    client_consents: Union[Unset, list['UserConsentRepresentation']] = UNSET
    not_before: Union[Unset, int] = UNSET
    application_roles: Union[Unset, 'UserRepresentationApplicationRoles'] = UNSET
    social_links: Union[Unset, list['SocialLinkRepresentation']] = UNSET
    groups: Union[Unset, list[str]] = UNSET
    access: Union[Unset, 'UserRepresentationAccess'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_representation_application_roles import UserRepresentationApplicationRoles
        from ..models.user_representation_client_roles import UserRepresentationClientRoles
        from ..models.user_profile_metadata import UserProfileMetadata
        from ..models.user_representation_attributes import UserRepresentationAttributes
        from ..models.federated_identity_representation import FederatedIdentityRepresentation
        from ..models.user_representation_access import UserRepresentationAccess
        from ..models.credential_representation import CredentialRepresentation
        from ..models.user_consent_representation import UserConsentRepresentation
        from ..models.social_link_representation import SocialLinkRepresentation
        id = self.id

        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        email = self.email

        email_verified = self.email_verified

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        user_profile_metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user_profile_metadata, Unset):
            user_profile_metadata = self.user_profile_metadata.to_dict()

        enabled = self.enabled

        self_ = self.self_

        origin = self.origin

        created_timestamp = self.created_timestamp

        totp = self.totp

        federation_link = self.federation_link

        service_account_client_id = self.service_account_client_id

        credentials: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.credentials, Unset):
            credentials = []
            for credentials_item_data in self.credentials:
                credentials_item = credentials_item_data.to_dict()
                credentials.append(credentials_item)



        disableable_credential_types: Union[Unset, list[str]] = UNSET
        if not isinstance(self.disableable_credential_types, Unset):
            disableable_credential_types = self.disableable_credential_types



        required_actions: Union[Unset, list[str]] = UNSET
        if not isinstance(self.required_actions, Unset):
            required_actions = self.required_actions



        federated_identities: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.federated_identities, Unset):
            federated_identities = []
            for federated_identities_item_data in self.federated_identities:
                federated_identities_item = federated_identities_item_data.to_dict()
                federated_identities.append(federated_identities_item)



        realm_roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.realm_roles, Unset):
            realm_roles = self.realm_roles



        client_roles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.client_roles, Unset):
            client_roles = self.client_roles.to_dict()

        client_consents: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.client_consents, Unset):
            client_consents = []
            for client_consents_item_data in self.client_consents:
                client_consents_item = client_consents_item_data.to_dict()
                client_consents.append(client_consents_item)



        not_before = self.not_before

        application_roles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.application_roles, Unset):
            application_roles = self.application_roles.to_dict()

        social_links: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.social_links, Unset):
            social_links = []
            for social_links_item_data in self.social_links:
                social_links_item = social_links_item_data.to_dict()
                social_links.append(social_links_item)



        groups: Union[Unset, list[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups



        access: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.access, Unset):
            access = self.access.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if username is not UNSET:
            field_dict["username"] = username
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if email is not UNSET:
            field_dict["email"] = email
        if email_verified is not UNSET:
            field_dict["emailVerified"] = email_verified
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if user_profile_metadata is not UNSET:
            field_dict["userProfileMetadata"] = user_profile_metadata
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if self_ is not UNSET:
            field_dict["self"] = self_
        if origin is not UNSET:
            field_dict["origin"] = origin
        if created_timestamp is not UNSET:
            field_dict["createdTimestamp"] = created_timestamp
        if totp is not UNSET:
            field_dict["totp"] = totp
        if federation_link is not UNSET:
            field_dict["federationLink"] = federation_link
        if service_account_client_id is not UNSET:
            field_dict["serviceAccountClientId"] = service_account_client_id
        if credentials is not UNSET:
            field_dict["credentials"] = credentials
        if disableable_credential_types is not UNSET:
            field_dict["disableableCredentialTypes"] = disableable_credential_types
        if required_actions is not UNSET:
            field_dict["requiredActions"] = required_actions
        if federated_identities is not UNSET:
            field_dict["federatedIdentities"] = federated_identities
        if realm_roles is not UNSET:
            field_dict["realmRoles"] = realm_roles
        if client_roles is not UNSET:
            field_dict["clientRoles"] = client_roles
        if client_consents is not UNSET:
            field_dict["clientConsents"] = client_consents
        if not_before is not UNSET:
            field_dict["notBefore"] = not_before
        if application_roles is not UNSET:
            field_dict["applicationRoles"] = application_roles
        if social_links is not UNSET:
            field_dict["socialLinks"] = social_links
        if groups is not UNSET:
            field_dict["groups"] = groups
        if access is not UNSET:
            field_dict["access"] = access

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_representation_application_roles import UserRepresentationApplicationRoles
        from ..models.user_representation_client_roles import UserRepresentationClientRoles
        from ..models.user_profile_metadata import UserProfileMetadata
        from ..models.user_representation_attributes import UserRepresentationAttributes
        from ..models.federated_identity_representation import FederatedIdentityRepresentation
        from ..models.user_representation_access import UserRepresentationAccess
        from ..models.credential_representation import CredentialRepresentation
        from ..models.user_consent_representation import UserConsentRepresentation
        from ..models.social_link_representation import SocialLinkRepresentation
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        username = d.pop("username", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        email = d.pop("email", UNSET)

        email_verified = d.pop("emailVerified", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, UserRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = UserRepresentationAttributes.from_dict(_attributes)




        _user_profile_metadata = d.pop("userProfileMetadata", UNSET)
        user_profile_metadata: Union[Unset, UserProfileMetadata]
        if isinstance(_user_profile_metadata,  Unset):
            user_profile_metadata = UNSET
        else:
            user_profile_metadata = UserProfileMetadata.from_dict(_user_profile_metadata)




        enabled = d.pop("enabled", UNSET)

        self_ = d.pop("self", UNSET)

        origin = d.pop("origin", UNSET)

        created_timestamp = d.pop("createdTimestamp", UNSET)

        totp = d.pop("totp", UNSET)

        federation_link = d.pop("federationLink", UNSET)

        service_account_client_id = d.pop("serviceAccountClientId", UNSET)

        credentials = []
        _credentials = d.pop("credentials", UNSET)
        for credentials_item_data in (_credentials or []):
            credentials_item = CredentialRepresentation.from_dict(credentials_item_data)



            credentials.append(credentials_item)


        disableable_credential_types = cast(list[str], d.pop("disableableCredentialTypes", UNSET))


        required_actions = cast(list[str], d.pop("requiredActions", UNSET))


        federated_identities = []
        _federated_identities = d.pop("federatedIdentities", UNSET)
        for federated_identities_item_data in (_federated_identities or []):
            federated_identities_item = FederatedIdentityRepresentation.from_dict(federated_identities_item_data)



            federated_identities.append(federated_identities_item)


        realm_roles = cast(list[str], d.pop("realmRoles", UNSET))


        _client_roles = d.pop("clientRoles", UNSET)
        client_roles: Union[Unset, UserRepresentationClientRoles]
        if isinstance(_client_roles,  Unset):
            client_roles = UNSET
        else:
            client_roles = UserRepresentationClientRoles.from_dict(_client_roles)




        client_consents = []
        _client_consents = d.pop("clientConsents", UNSET)
        for client_consents_item_data in (_client_consents or []):
            client_consents_item = UserConsentRepresentation.from_dict(client_consents_item_data)



            client_consents.append(client_consents_item)


        not_before = d.pop("notBefore", UNSET)

        _application_roles = d.pop("applicationRoles", UNSET)
        application_roles: Union[Unset, UserRepresentationApplicationRoles]
        if isinstance(_application_roles,  Unset):
            application_roles = UNSET
        else:
            application_roles = UserRepresentationApplicationRoles.from_dict(_application_roles)




        social_links = []
        _social_links = d.pop("socialLinks", UNSET)
        for social_links_item_data in (_social_links or []):
            social_links_item = SocialLinkRepresentation.from_dict(social_links_item_data)



            social_links.append(social_links_item)


        groups = cast(list[str], d.pop("groups", UNSET))


        _access = d.pop("access", UNSET)
        access: Union[Unset, UserRepresentationAccess]
        if isinstance(_access,  Unset):
            access = UNSET
        else:
            access = UserRepresentationAccess.from_dict(_access)




        user_representation = cls(
            id=id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            email_verified=email_verified,
            attributes=attributes,
            user_profile_metadata=user_profile_metadata,
            enabled=enabled,
            self_=self_,
            origin=origin,
            created_timestamp=created_timestamp,
            totp=totp,
            federation_link=federation_link,
            service_account_client_id=service_account_client_id,
            credentials=credentials,
            disableable_credential_types=disableable_credential_types,
            required_actions=required_actions,
            federated_identities=federated_identities,
            realm_roles=realm_roles,
            client_roles=client_roles,
            client_consents=client_consents,
            not_before=not_before,
            application_roles=application_roles,
            social_links=social_links,
            groups=groups,
            access=access,
        )


        user_representation.additional_properties = d
        return user_representation

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
