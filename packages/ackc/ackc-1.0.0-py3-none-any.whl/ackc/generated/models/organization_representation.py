from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.organization_domain_representation import OrganizationDomainRepresentation
  from ..models.member_representation import MemberRepresentation
  from ..models.identity_provider_representation import IdentityProviderRepresentation
  from ..models.organization_representation_attributes import OrganizationRepresentationAttributes





T = TypeVar("T", bound="OrganizationRepresentation")



@_attrs_define
class OrganizationRepresentation:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            alias (Union[Unset, str]):
            enabled (Union[Unset, bool]):
            description (Union[Unset, str]):
            redirect_url (Union[Unset, str]):
            attributes (Union[Unset, OrganizationRepresentationAttributes]):
            domains (Union[Unset, list['OrganizationDomainRepresentation']]):
            members (Union[Unset, list['MemberRepresentation']]):
            identity_providers (Union[Unset, list['IdentityProviderRepresentation']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    alias: Union[Unset, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    redirect_url: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'OrganizationRepresentationAttributes'] = UNSET
    domains: Union[Unset, list['OrganizationDomainRepresentation']] = UNSET
    members: Union[Unset, list['MemberRepresentation']] = UNSET
    identity_providers: Union[Unset, list['IdentityProviderRepresentation']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.organization_domain_representation import OrganizationDomainRepresentation
        from ..models.member_representation import MemberRepresentation
        from ..models.identity_provider_representation import IdentityProviderRepresentation
        from ..models.organization_representation_attributes import OrganizationRepresentationAttributes
        id = self.id

        name = self.name

        alias = self.alias

        enabled = self.enabled

        description = self.description

        redirect_url = self.redirect_url

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        domains: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.domains, Unset):
            domains = []
            for domains_item_data in self.domains:
                domains_item = domains_item_data.to_dict()
                domains.append(domains_item)



        members: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)



        identity_providers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.identity_providers, Unset):
            identity_providers = []
            for identity_providers_item_data in self.identity_providers:
                identity_providers_item = identity_providers_item_data.to_dict()
                identity_providers.append(identity_providers_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if alias is not UNSET:
            field_dict["alias"] = alias
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if description is not UNSET:
            field_dict["description"] = description
        if redirect_url is not UNSET:
            field_dict["redirectUrl"] = redirect_url
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if domains is not UNSET:
            field_dict["domains"] = domains
        if members is not UNSET:
            field_dict["members"] = members
        if identity_providers is not UNSET:
            field_dict["identityProviders"] = identity_providers

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization_domain_representation import OrganizationDomainRepresentation
        from ..models.member_representation import MemberRepresentation
        from ..models.identity_provider_representation import IdentityProviderRepresentation
        from ..models.organization_representation_attributes import OrganizationRepresentationAttributes
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        alias = d.pop("alias", UNSET)

        enabled = d.pop("enabled", UNSET)

        description = d.pop("description", UNSET)

        redirect_url = d.pop("redirectUrl", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, OrganizationRepresentationAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = OrganizationRepresentationAttributes.from_dict(_attributes)




        domains = []
        _domains = d.pop("domains", UNSET)
        for domains_item_data in (_domains or []):
            domains_item = OrganizationDomainRepresentation.from_dict(domains_item_data)



            domains.append(domains_item)


        members = []
        _members = d.pop("members", UNSET)
        for members_item_data in (_members or []):
            members_item = MemberRepresentation.from_dict(members_item_data)



            members.append(members_item)


        identity_providers = []
        _identity_providers = d.pop("identityProviders", UNSET)
        for identity_providers_item_data in (_identity_providers or []):
            identity_providers_item = IdentityProviderRepresentation.from_dict(identity_providers_item_data)



            identity_providers.append(identity_providers_item)


        organization_representation = cls(
            id=id,
            name=name,
            alias=alias,
            enabled=enabled,
            description=description,
            redirect_url=redirect_url,
            attributes=attributes,
            domains=domains,
            members=members,
            identity_providers=identity_providers,
        )


        organization_representation.additional_properties = d
        return organization_representation

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
