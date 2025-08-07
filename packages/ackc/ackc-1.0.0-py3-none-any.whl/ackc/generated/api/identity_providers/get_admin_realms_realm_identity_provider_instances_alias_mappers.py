from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.identity_provider_mapper_representation import IdentityProviderMapperRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    alias: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/identity-provider/instances/{alias}/mappers".format(realm=realm,alias=alias,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['IdentityProviderMapperRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = IdentityProviderMapperRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['IdentityProviderMapperRepresentation']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['IdentityProviderMapperRepresentation']]:
    """ Get mappers for identity provider

    Args:
        realm (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['IdentityProviderMapperRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
alias=alias,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['IdentityProviderMapperRepresentation'] | None:
    """ Get mappers for identity provider

    Args:
        realm (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['IdentityProviderMapperRepresentation']
     """


    return sync_detailed(
        realm=realm,
alias=alias,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['IdentityProviderMapperRepresentation']]:
    """ Get mappers for identity provider

    Args:
        realm (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['IdentityProviderMapperRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
alias=alias,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['IdentityProviderMapperRepresentation'] | None:
    """ Get mappers for identity provider

    Args:
        realm (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['IdentityProviderMapperRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
alias=alias,
client=client,

    )).parsed
