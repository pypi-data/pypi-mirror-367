from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    realm: str,
    locale: str,
    key: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/localization/{locale}/{key}".format(realm=realm,locale=locale,key=key,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, str] | None:
    if response.status_code == 200:
        response_200 = response.text
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


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    locale: str,
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, str]]:
    """ 
    Args:
        realm (str):
        locale (str):
        key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
     """


    kwargs = _get_kwargs(
        realm=realm,
locale=locale,
key=key,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    locale: str,
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, str] | None:
    """ 
    Args:
        realm (str):
        locale (str):
        key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, str]
     """


    return sync_detailed(
        realm=realm,
locale=locale,
key=key,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    locale: str,
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, str]]:
    """ 
    Args:
        realm (str):
        locale (str):
        key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
     """


    kwargs = _get_kwargs(
        realm=realm,
locale=locale,
key=key,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    locale: str,
    key: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, str] | None:
    """ 
    Args:
        realm (str):
        locale (str):
        key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, str]
     """


    return (await asyncio_detailed(
        realm=realm,
locale=locale,
key=key,
client=client,

    )).parsed
