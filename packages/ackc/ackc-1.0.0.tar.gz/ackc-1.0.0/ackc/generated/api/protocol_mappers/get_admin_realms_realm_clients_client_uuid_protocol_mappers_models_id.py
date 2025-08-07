from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.protocol_mapper_representation import ProtocolMapperRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    client_uuid: str,
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/protocol-mappers/models/{id}".format(realm=realm,client_uuid=client_uuid,id=id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ProtocolMapperRepresentation | None:
    if response.status_code == 200:
        response_200 = ProtocolMapperRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ProtocolMapperRepresentation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_uuid: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ProtocolMapperRepresentation]:
    """ Get mapper by id

    Args:
        realm (str):
        client_uuid (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProtocolMapperRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
id=id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    client_uuid: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> ProtocolMapperRepresentation | None:
    """ Get mapper by id

    Args:
        realm (str):
        client_uuid (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProtocolMapperRepresentation
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
id=id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ProtocolMapperRepresentation]:
    """ Get mapper by id

    Args:
        realm (str):
        client_uuid (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProtocolMapperRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
id=id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    client_uuid: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> ProtocolMapperRepresentation | None:
    """ Get mapper by id

    Args:
        realm (str):
        client_uuid (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProtocolMapperRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
id=id,
client=client,

    )).parsed
