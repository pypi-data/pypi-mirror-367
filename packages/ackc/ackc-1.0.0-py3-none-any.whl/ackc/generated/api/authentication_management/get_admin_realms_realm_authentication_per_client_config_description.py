from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_authentication_per_client_config_description_response_200 import GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200
from typing import cast



def _get_kwargs(
    realm: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/authentication/per-client-config-description".format(realm=realm,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200 | None:
    if response.status_code == 200:
        response_200 = GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200]:
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

) -> Response[GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200]:
    """ Get configuration descriptions for all clients

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200]
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

) -> GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200 | None:
    """ Get configuration descriptions for all clients

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200
     """


    return sync_detailed(
        realm=realm,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200]:
    """ Get configuration descriptions for all clients

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200]
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

) -> GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200 | None:
    """ Get configuration descriptions for all clients

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminRealmsRealmAuthenticationPerClientConfigDescriptionResponse200
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,

    )).parsed
