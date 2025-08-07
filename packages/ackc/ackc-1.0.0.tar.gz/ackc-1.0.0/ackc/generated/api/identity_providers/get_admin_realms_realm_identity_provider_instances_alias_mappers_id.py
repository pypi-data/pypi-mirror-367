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
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/identity-provider/instances/{alias}/mappers/{id}".format(realm=realm,alias=alias,id=id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> IdentityProviderMapperRepresentation | None:
    if response.status_code == 200:
        response_200 = IdentityProviderMapperRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[IdentityProviderMapperRepresentation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    alias: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[IdentityProviderMapperRepresentation]:
    """ Get mapper by id for the identity provider

    Args:
        realm (str):
        alias (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IdentityProviderMapperRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
alias=alias,
id=id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    alias: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> IdentityProviderMapperRepresentation | None:
    """ Get mapper by id for the identity provider

    Args:
        realm (str):
        alias (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IdentityProviderMapperRepresentation
     """


    return sync_detailed(
        realm=realm,
alias=alias,
id=id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    alias: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[IdentityProviderMapperRepresentation]:
    """ Get mapper by id for the identity provider

    Args:
        realm (str):
        alias (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IdentityProviderMapperRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
alias=alias,
id=id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    alias: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> IdentityProviderMapperRepresentation | None:
    """ Get mapper by id for the identity provider

    Args:
        realm (str):
        alias (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IdentityProviderMapperRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
alias=alias,
id=id,
client=client,

    )).parsed
