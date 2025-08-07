from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.client_initial_access_create_presentation import ClientInitialAccessCreatePresentation
from typing import cast



def _get_kwargs(
    realm: str,
    *,
    body: ClientInitialAccessCreatePresentation,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/clients-initial-access".format(realm=realm,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ClientInitialAccessCreatePresentation | None:
    if response.status_code == 201:
        response_201 = ClientInitialAccessCreatePresentation.from_dict(response.json())



        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ClientInitialAccessCreatePresentation]:
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
    body: ClientInitialAccessCreatePresentation,

) -> Response[ClientInitialAccessCreatePresentation]:
    """ Create a new initial access token.

    Args:
        realm (str):
        body (ClientInitialAccessCreatePresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientInitialAccessCreatePresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClientInitialAccessCreatePresentation,

) -> ClientInitialAccessCreatePresentation | None:
    """ Create a new initial access token.

    Args:
        realm (str):
        body (ClientInitialAccessCreatePresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientInitialAccessCreatePresentation
     """


    return sync_detailed(
        realm=realm,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClientInitialAccessCreatePresentation,

) -> Response[ClientInitialAccessCreatePresentation]:
    """ Create a new initial access token.

    Args:
        realm (str):
        body (ClientInitialAccessCreatePresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientInitialAccessCreatePresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClientInitialAccessCreatePresentation,

) -> ClientInitialAccessCreatePresentation | None:
    """ Create a new initial access token.

    Args:
        realm (str):
        body (ClientInitialAccessCreatePresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientInitialAccessCreatePresentation
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
body=body,

    )).parsed
