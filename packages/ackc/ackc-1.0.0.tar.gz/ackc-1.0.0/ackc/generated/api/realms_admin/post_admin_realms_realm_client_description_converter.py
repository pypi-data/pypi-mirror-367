from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.client_representation import ClientRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    *,
    body: str,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/client-description-converter".format(realm=realm,),
    }

    _kwargs["json"] = body



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, ClientRepresentation] | None:
    if response.status_code == 200:
        response_200 = ClientRepresentation.from_dict(response.json())



        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, ClientRepresentation]]:
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
    body: str,

) -> Response[Union[Any, ClientRepresentation]]:
    """ Base path for importing clients under this realm.

    Args:
        realm (str):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ClientRepresentation]]
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
    body: str,

) -> Union[Any, ClientRepresentation] | None:
    """ Base path for importing clients under this realm.

    Args:
        realm (str):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ClientRepresentation]
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
    body: str,

) -> Response[Union[Any, ClientRepresentation]]:
    """ Base path for importing clients under this realm.

    Args:
        realm (str):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ClientRepresentation]]
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
    body: str,

) -> Union[Any, ClientRepresentation] | None:
    """ Base path for importing clients under this realm.

    Args:
        realm (str):
        body (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ClientRepresentation]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
body=body,

    )).parsed
