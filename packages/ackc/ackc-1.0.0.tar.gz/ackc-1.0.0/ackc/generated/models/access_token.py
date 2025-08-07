from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.authorization import Authorization
  from ..models.access_token_resource_access import AccessTokenResourceAccess
  from ..models.access_token_other_claims import AccessTokenOtherClaims
  from ..models.access import Access
  from ..models.address_claim_set import AddressClaimSet
  from ..models.confirmation import Confirmation





T = TypeVar("T", bound="AccessToken")



@_attrs_define
class AccessToken:
    """ 
        Attributes:
            jti (Union[Unset, str]):
            exp (Union[Unset, int]):
            nbf (Union[Unset, int]):
            iat (Union[Unset, int]):
            iss (Union[Unset, str]):
            sub (Union[Unset, str]):
            typ (Union[Unset, str]):
            azp (Union[Unset, str]):
            other_claims (Union[Unset, AccessTokenOtherClaims]):
            nonce (Union[Unset, str]):
            auth_time (Union[Unset, int]):
            sid (Union[Unset, str]):
            at_hash (Union[Unset, str]):
            c_hash (Union[Unset, str]):
            name (Union[Unset, str]):
            given_name (Union[Unset, str]):
            family_name (Union[Unset, str]):
            middle_name (Union[Unset, str]):
            nickname (Union[Unset, str]):
            preferred_username (Union[Unset, str]):
            profile (Union[Unset, str]):
            picture (Union[Unset, str]):
            website (Union[Unset, str]):
            email (Union[Unset, str]):
            email_verified (Union[Unset, bool]):
            gender (Union[Unset, str]):
            birthdate (Union[Unset, str]):
            zoneinfo (Union[Unset, str]):
            locale (Union[Unset, str]):
            phone_number (Union[Unset, str]):
            phone_number_verified (Union[Unset, bool]):
            address (Union[Unset, AddressClaimSet]):
            updated_at (Union[Unset, int]):
            claims_locales (Union[Unset, str]):
            acr (Union[Unset, str]):
            s_hash (Union[Unset, str]):
            trusted_certs (Union[Unset, list[str]]):
            allowed_origins (Union[Unset, list[str]]):
            realm_access (Union[Unset, Access]):
            resource_access (Union[Unset, AccessTokenResourceAccess]):
            authorization (Union[Unset, Authorization]):
            cnf (Union[Unset, Confirmation]):
            scope (Union[Unset, str]):
     """

    jti: Union[Unset, str] = UNSET
    exp: Union[Unset, int] = UNSET
    nbf: Union[Unset, int] = UNSET
    iat: Union[Unset, int] = UNSET
    iss: Union[Unset, str] = UNSET
    sub: Union[Unset, str] = UNSET
    typ: Union[Unset, str] = UNSET
    azp: Union[Unset, str] = UNSET
    other_claims: Union[Unset, 'AccessTokenOtherClaims'] = UNSET
    nonce: Union[Unset, str] = UNSET
    auth_time: Union[Unset, int] = UNSET
    sid: Union[Unset, str] = UNSET
    at_hash: Union[Unset, str] = UNSET
    c_hash: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    given_name: Union[Unset, str] = UNSET
    family_name: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    preferred_username: Union[Unset, str] = UNSET
    profile: Union[Unset, str] = UNSET
    picture: Union[Unset, str] = UNSET
    website: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    email_verified: Union[Unset, bool] = UNSET
    gender: Union[Unset, str] = UNSET
    birthdate: Union[Unset, str] = UNSET
    zoneinfo: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    phone_number: Union[Unset, str] = UNSET
    phone_number_verified: Union[Unset, bool] = UNSET
    address: Union[Unset, 'AddressClaimSet'] = UNSET
    updated_at: Union[Unset, int] = UNSET
    claims_locales: Union[Unset, str] = UNSET
    acr: Union[Unset, str] = UNSET
    s_hash: Union[Unset, str] = UNSET
    trusted_certs: Union[Unset, list[str]] = UNSET
    allowed_origins: Union[Unset, list[str]] = UNSET
    realm_access: Union[Unset, 'Access'] = UNSET
    resource_access: Union[Unset, 'AccessTokenResourceAccess'] = UNSET
    authorization: Union[Unset, 'Authorization'] = UNSET
    cnf: Union[Unset, 'Confirmation'] = UNSET
    scope: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.authorization import Authorization
        from ..models.access_token_resource_access import AccessTokenResourceAccess
        from ..models.access_token_other_claims import AccessTokenOtherClaims
        from ..models.access import Access
        from ..models.address_claim_set import AddressClaimSet
        from ..models.confirmation import Confirmation
        jti = self.jti

        exp = self.exp

        nbf = self.nbf

        iat = self.iat

        iss = self.iss

        sub = self.sub

        typ = self.typ

        azp = self.azp

        other_claims: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.other_claims, Unset):
            other_claims = self.other_claims.to_dict()

        nonce = self.nonce

        auth_time = self.auth_time

        sid = self.sid

        at_hash = self.at_hash

        c_hash = self.c_hash

        name = self.name

        given_name = self.given_name

        family_name = self.family_name

        middle_name = self.middle_name

        nickname = self.nickname

        preferred_username = self.preferred_username

        profile = self.profile

        picture = self.picture

        website = self.website

        email = self.email

        email_verified = self.email_verified

        gender = self.gender

        birthdate = self.birthdate

        zoneinfo = self.zoneinfo

        locale = self.locale

        phone_number = self.phone_number

        phone_number_verified = self.phone_number_verified

        address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.address, Unset):
            address = self.address.to_dict()

        updated_at = self.updated_at

        claims_locales = self.claims_locales

        acr = self.acr

        s_hash = self.s_hash

        trusted_certs: Union[Unset, list[str]] = UNSET
        if not isinstance(self.trusted_certs, Unset):
            trusted_certs = self.trusted_certs



        allowed_origins: Union[Unset, list[str]] = UNSET
        if not isinstance(self.allowed_origins, Unset):
            allowed_origins = self.allowed_origins



        realm_access: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.realm_access, Unset):
            realm_access = self.realm_access.to_dict()

        resource_access: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.resource_access, Unset):
            resource_access = self.resource_access.to_dict()

        authorization: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authorization, Unset):
            authorization = self.authorization.to_dict()

        cnf: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cnf, Unset):
            cnf = self.cnf.to_dict()

        scope = self.scope


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if jti is not UNSET:
            field_dict["jti"] = jti
        if exp is not UNSET:
            field_dict["exp"] = exp
        if nbf is not UNSET:
            field_dict["nbf"] = nbf
        if iat is not UNSET:
            field_dict["iat"] = iat
        if iss is not UNSET:
            field_dict["iss"] = iss
        if sub is not UNSET:
            field_dict["sub"] = sub
        if typ is not UNSET:
            field_dict["typ"] = typ
        if azp is not UNSET:
            field_dict["azp"] = azp
        if other_claims is not UNSET:
            field_dict["otherClaims"] = other_claims
        if nonce is not UNSET:
            field_dict["nonce"] = nonce
        if auth_time is not UNSET:
            field_dict["auth_time"] = auth_time
        if sid is not UNSET:
            field_dict["sid"] = sid
        if at_hash is not UNSET:
            field_dict["at_hash"] = at_hash
        if c_hash is not UNSET:
            field_dict["c_hash"] = c_hash
        if name is not UNSET:
            field_dict["name"] = name
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if family_name is not UNSET:
            field_dict["family_name"] = family_name
        if middle_name is not UNSET:
            field_dict["middle_name"] = middle_name
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if preferred_username is not UNSET:
            field_dict["preferred_username"] = preferred_username
        if profile is not UNSET:
            field_dict["profile"] = profile
        if picture is not UNSET:
            field_dict["picture"] = picture
        if website is not UNSET:
            field_dict["website"] = website
        if email is not UNSET:
            field_dict["email"] = email
        if email_verified is not UNSET:
            field_dict["email_verified"] = email_verified
        if gender is not UNSET:
            field_dict["gender"] = gender
        if birthdate is not UNSET:
            field_dict["birthdate"] = birthdate
        if zoneinfo is not UNSET:
            field_dict["zoneinfo"] = zoneinfo
        if locale is not UNSET:
            field_dict["locale"] = locale
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if phone_number_verified is not UNSET:
            field_dict["phone_number_verified"] = phone_number_verified
        if address is not UNSET:
            field_dict["address"] = address
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if claims_locales is not UNSET:
            field_dict["claims_locales"] = claims_locales
        if acr is not UNSET:
            field_dict["acr"] = acr
        if s_hash is not UNSET:
            field_dict["s_hash"] = s_hash
        if trusted_certs is not UNSET:
            field_dict["trusted-certs"] = trusted_certs
        if allowed_origins is not UNSET:
            field_dict["allowed-origins"] = allowed_origins
        if realm_access is not UNSET:
            field_dict["realm_access"] = realm_access
        if resource_access is not UNSET:
            field_dict["resource_access"] = resource_access
        if authorization is not UNSET:
            field_dict["authorization"] = authorization
        if cnf is not UNSET:
            field_dict["cnf"] = cnf
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization import Authorization
        from ..models.access_token_resource_access import AccessTokenResourceAccess
        from ..models.access_token_other_claims import AccessTokenOtherClaims
        from ..models.access import Access
        from ..models.address_claim_set import AddressClaimSet
        from ..models.confirmation import Confirmation
        d = dict(src_dict)
        jti = d.pop("jti", UNSET)

        exp = d.pop("exp", UNSET)

        nbf = d.pop("nbf", UNSET)

        iat = d.pop("iat", UNSET)

        iss = d.pop("iss", UNSET)

        sub = d.pop("sub", UNSET)

        typ = d.pop("typ", UNSET)

        azp = d.pop("azp", UNSET)

        _other_claims = d.pop("otherClaims", UNSET)
        other_claims: Union[Unset, AccessTokenOtherClaims]
        if isinstance(_other_claims,  Unset):
            other_claims = UNSET
        else:
            other_claims = AccessTokenOtherClaims.from_dict(_other_claims)




        nonce = d.pop("nonce", UNSET)

        auth_time = d.pop("auth_time", UNSET)

        sid = d.pop("sid", UNSET)

        at_hash = d.pop("at_hash", UNSET)

        c_hash = d.pop("c_hash", UNSET)

        name = d.pop("name", UNSET)

        given_name = d.pop("given_name", UNSET)

        family_name = d.pop("family_name", UNSET)

        middle_name = d.pop("middle_name", UNSET)

        nickname = d.pop("nickname", UNSET)

        preferred_username = d.pop("preferred_username", UNSET)

        profile = d.pop("profile", UNSET)

        picture = d.pop("picture", UNSET)

        website = d.pop("website", UNSET)

        email = d.pop("email", UNSET)

        email_verified = d.pop("email_verified", UNSET)

        gender = d.pop("gender", UNSET)

        birthdate = d.pop("birthdate", UNSET)

        zoneinfo = d.pop("zoneinfo", UNSET)

        locale = d.pop("locale", UNSET)

        phone_number = d.pop("phone_number", UNSET)

        phone_number_verified = d.pop("phone_number_verified", UNSET)

        _address = d.pop("address", UNSET)
        address: Union[Unset, AddressClaimSet]
        if isinstance(_address,  Unset):
            address = UNSET
        else:
            address = AddressClaimSet.from_dict(_address)




        updated_at = d.pop("updated_at", UNSET)

        claims_locales = d.pop("claims_locales", UNSET)

        acr = d.pop("acr", UNSET)

        s_hash = d.pop("s_hash", UNSET)

        trusted_certs = cast(list[str], d.pop("trusted-certs", UNSET))


        allowed_origins = cast(list[str], d.pop("allowed-origins", UNSET))


        _realm_access = d.pop("realm_access", UNSET)
        realm_access: Union[Unset, Access]
        if isinstance(_realm_access,  Unset):
            realm_access = UNSET
        else:
            realm_access = Access.from_dict(_realm_access)




        _resource_access = d.pop("resource_access", UNSET)
        resource_access: Union[Unset, AccessTokenResourceAccess]
        if isinstance(_resource_access,  Unset):
            resource_access = UNSET
        else:
            resource_access = AccessTokenResourceAccess.from_dict(_resource_access)




        _authorization = d.pop("authorization", UNSET)
        authorization: Union[Unset, Authorization]
        if isinstance(_authorization,  Unset):
            authorization = UNSET
        else:
            authorization = Authorization.from_dict(_authorization)




        _cnf = d.pop("cnf", UNSET)
        cnf: Union[Unset, Confirmation]
        if isinstance(_cnf,  Unset):
            cnf = UNSET
        else:
            cnf = Confirmation.from_dict(_cnf)




        scope = d.pop("scope", UNSET)

        access_token = cls(
            jti=jti,
            exp=exp,
            nbf=nbf,
            iat=iat,
            iss=iss,
            sub=sub,
            typ=typ,
            azp=azp,
            other_claims=other_claims,
            nonce=nonce,
            auth_time=auth_time,
            sid=sid,
            at_hash=at_hash,
            c_hash=c_hash,
            name=name,
            given_name=given_name,
            family_name=family_name,
            middle_name=middle_name,
            nickname=nickname,
            preferred_username=preferred_username,
            profile=profile,
            picture=picture,
            website=website,
            email=email,
            email_verified=email_verified,
            gender=gender,
            birthdate=birthdate,
            zoneinfo=zoneinfo,
            locale=locale,
            phone_number=phone_number,
            phone_number_verified=phone_number_verified,
            address=address,
            updated_at=updated_at,
            claims_locales=claims_locales,
            acr=acr,
            s_hash=s_hash,
            trusted_certs=trusted_certs,
            allowed_origins=allowed_origins,
            realm_access=realm_access,
            resource_access=resource_access,
            authorization=authorization,
            cnf=cnf,
            scope=scope,
        )


        access_token.additional_properties = d
        return access_token

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
