from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_identity_provider_providers_provider_id_response_200 import GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200
from typing import cast



def _get_kwargs(
    realm: str,
    provider_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/identity-provider/providers/{provider_id}".format(realm=realm,provider_id=provider_id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200 | None:
    if response.status_code == 200:
        response_200 = GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    provider_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200]:
    """ Get the identity provider factory for that provider id

    Args:
        realm (str):
        provider_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200]
     """


    kwargs = _get_kwargs(
        realm=realm,
provider_id=provider_id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    provider_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200 | None:
    """ Get the identity provider factory for that provider id

    Args:
        realm (str):
        provider_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200
     """


    return sync_detailed(
        realm=realm,
provider_id=provider_id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    provider_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200]:
    """ Get the identity provider factory for that provider id

    Args:
        realm (str):
        provider_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200]
     """


    kwargs = _get_kwargs(
        realm=realm,
provider_id=provider_id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    provider_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200 | None:
    """ Get the identity provider factory for that provider id

    Args:
        realm (str):
        provider_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminRealmsRealmIdentityProviderProvidersProviderIdResponse200
     """


    return (await asyncio_detailed(
        realm=realm,
provider_id=provider_id,
client=client,

    )).parsed
