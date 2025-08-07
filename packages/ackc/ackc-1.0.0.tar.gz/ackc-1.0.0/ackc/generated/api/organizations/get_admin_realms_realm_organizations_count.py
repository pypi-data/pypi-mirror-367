from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    exact: Union[Unset, bool] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["exact"] = exact

    params["q"] = q

    params["search"] = search


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/organizations/count".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> int | None:
    if response.status_code == 200:
        response_200 = cast(int, response.json())
        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[int]:
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
    exact: Union[Unset, bool] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> Response[int]:
    """ Returns the organizations counts.

    Args:
        realm (str):
        exact (Union[Unset, bool]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[int]
     """


    kwargs = _get_kwargs(
        realm=realm,
exact=exact,
q=q,
search=search,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> int | None:
    """ Returns the organizations counts.

    Args:
        realm (str):
        exact (Union[Unset, bool]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        int
     """


    return sync_detailed(
        realm=realm,
client=client,
exact=exact,
q=q,
search=search,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> Response[int]:
    """ Returns the organizations counts.

    Args:
        realm (str):
        exact (Union[Unset, bool]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[int]
     """


    kwargs = _get_kwargs(
        realm=realm,
exact=exact,
q=q,
search=search,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> int | None:
    """ Returns the organizations counts.

    Args:
        realm (str):
        exact (Union[Unset, bool]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        int
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
exact=exact,
q=q,
search=search,

    )).parsed
