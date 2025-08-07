from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_authentication_client_authenticator_providers_response_200_item import GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item
from typing import cast



def _get_kwargs(
    realm: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/authentication/client-authenticator-providers".format(realm=realm,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']]:
    """ Get client authenticator providers Returns a stream of client authenticator providers.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']]
     """


    kwargs = _get_kwargs(
        realm=realm,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item'] | None:
    """ Get client authenticator providers Returns a stream of client authenticator providers.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']
     """


    return sync_detailed(
        realm=realm,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']]:
    """ Get client authenticator providers Returns a stream of client authenticator providers.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']]
     """


    kwargs = _get_kwargs(
        realm=realm,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item'] | None:
    """ Get client authenticator providers Returns a stream of client authenticator providers.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GetAdminRealmsRealmAuthenticationClientAuthenticatorProvidersResponse200Item']
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,

    )).parsed
