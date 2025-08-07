from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.client_types_representation import ClientTypesRepresentation
from typing import cast



def _get_kwargs(
    realm: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/client-types".format(realm=realm,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ClientTypesRepresentation | None:
    if response.status_code == 200:
        response_200 = ClientTypesRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ClientTypesRepresentation]:
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

) -> Response[ClientTypesRepresentation]:
    """ List all client types available in the current realm

     This endpoint returns a list of both global and realm level client types and the attributes they set

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientTypesRepresentation]
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

) -> ClientTypesRepresentation | None:
    """ List all client types available in the current realm

     This endpoint returns a list of both global and realm level client types and the attributes they set

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientTypesRepresentation
     """


    return sync_detailed(
        realm=realm,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ClientTypesRepresentation]:
    """ List all client types available in the current realm

     This endpoint returns a list of both global and realm level client types and the attributes they set

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientTypesRepresentation]
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

) -> ClientTypesRepresentation | None:
    """ List all client types available in the current realm

     This endpoint returns a list of both global and realm level client types and the attributes they set

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientTypesRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,

    )).parsed
