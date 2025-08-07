from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.component_representation import ComponentRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/components/{id}".format(realm=realm,id=id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ComponentRepresentation | None:
    if response.status_code == 200:
        response_200 = ComponentRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ComponentRepresentation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ComponentRepresentation]:
    """ 
    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ComponentRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
id=id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> ComponentRepresentation | None:
    """ 
    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ComponentRepresentation
     """


    return sync_detailed(
        realm=realm,
id=id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ComponentRepresentation]:
    """ 
    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ComponentRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
id=id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> ComponentRepresentation | None:
    """ 
    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ComponentRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
id=id,
client=client,

    )).parsed
