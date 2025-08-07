from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.role_representation import RoleRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    client_scope_id: str,
    client_path: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/client-templates/{client_scope_id}/scope-mappings/clients/{client_path}".format(realm=realm,client_scope_id=client_scope_id,client_path=client_path,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['RoleRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = RoleRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['RoleRepresentation']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_scope_id: str,
    client_path: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['RoleRepresentation']]:
    """ Get the roles associated with a client's scope Returns roles for the client.

    Args:
        realm (str):
        client_scope_id (str):
        client_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['RoleRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_scope_id=client_scope_id,
client_path=client_path,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    client_scope_id: str,
    client_path: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['RoleRepresentation'] | None:
    """ Get the roles associated with a client's scope Returns roles for the client.

    Args:
        realm (str):
        client_scope_id (str):
        client_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['RoleRepresentation']
     """


    return sync_detailed(
        realm=realm,
client_scope_id=client_scope_id,
client_path=client_path,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_scope_id: str,
    client_path: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['RoleRepresentation']]:
    """ Get the roles associated with a client's scope Returns roles for the client.

    Args:
        realm (str):
        client_scope_id (str):
        client_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['RoleRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_scope_id=client_scope_id,
client_path=client_path,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    client_scope_id: str,
    client_path: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['RoleRepresentation'] | None:
    """ Get the roles associated with a client's scope Returns roles for the client.

    Args:
        realm (str):
        client_scope_id (str):
        client_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['RoleRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
client_scope_id=client_scope_id,
client_path=client_path,
client=client,

    )).parsed
