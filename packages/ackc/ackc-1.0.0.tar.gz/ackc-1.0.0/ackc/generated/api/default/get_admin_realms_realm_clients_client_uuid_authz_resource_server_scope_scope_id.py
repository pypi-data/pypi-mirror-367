from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.scope_representation import ScopeRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    client_uuid: str,
    scope_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/scope/{scope_id}".format(realm=realm,client_uuid=client_uuid,scope_id=scope_id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, ScopeRepresentation] | None:
    if response.status_code == 200:
        response_200 = ScopeRepresentation.from_dict(response.json())



        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, ScopeRepresentation]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_uuid: str,
    scope_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, ScopeRepresentation]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ScopeRepresentation]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
scope_id=scope_id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    client_uuid: str,
    scope_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, ScopeRepresentation] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ScopeRepresentation]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
scope_id=scope_id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    scope_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, ScopeRepresentation]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ScopeRepresentation]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
scope_id=scope_id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    client_uuid: str,
    scope_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, ScopeRepresentation] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        scope_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ScopeRepresentation]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
scope_id=scope_id,
client=client,

    )).parsed
