from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.authentication_flow_representation import AuthenticationFlowRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/authentication/flows/{id}".format(realm=realm,id=id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> AuthenticationFlowRepresentation | None:
    if response.status_code == 200:
        response_200 = AuthenticationFlowRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[AuthenticationFlowRepresentation]:
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

) -> Response[AuthenticationFlowRepresentation]:
    """ Get authentication flow for id

    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticationFlowRepresentation]
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

) -> AuthenticationFlowRepresentation | None:
    """ Get authentication flow for id

    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticationFlowRepresentation
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

) -> Response[AuthenticationFlowRepresentation]:
    """ Get authentication flow for id

    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthenticationFlowRepresentation]
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

) -> AuthenticationFlowRepresentation | None:
    """ Get authentication flow for id

    Args:
        realm (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthenticationFlowRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
id=id,
client=client,

    )).parsed
