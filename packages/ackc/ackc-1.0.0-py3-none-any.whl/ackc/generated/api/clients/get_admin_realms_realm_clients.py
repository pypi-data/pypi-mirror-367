from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.client_representation import ClientRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    client_id: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, bool] = False,
    viewable_only: Union[Unset, bool] = False,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["clientId"] = client_id

    params["first"] = first

    params["max"] = max_

    params["q"] = q

    params["search"] = search

    params["viewableOnly"] = viewable_only


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['ClientRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = ClientRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['ClientRepresentation']]:
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
    client_id: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, bool] = False,
    viewable_only: Union[Unset, bool] = False,

) -> Response[list['ClientRepresentation']]:
    """ Get clients belonging to the realm.

     If a client can’t be retrieved from the storage due to a problem with the underlying storage, it is
    silently removed from the returned list. This ensures that concurrent modifications to the list
    don’t prevent callers from retrieving this list.

    Args:
        realm (str):
        client_id (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, bool]):  Default: False.
        viewable_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ClientRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_id=client_id,
first=first,
max_=max_,
q=q,
search=search,
viewable_only=viewable_only,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_id: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, bool] = False,
    viewable_only: Union[Unset, bool] = False,

) -> list['ClientRepresentation'] | None:
    """ Get clients belonging to the realm.

     If a client can’t be retrieved from the storage due to a problem with the underlying storage, it is
    silently removed from the returned list. This ensures that concurrent modifications to the list
    don’t prevent callers from retrieving this list.

    Args:
        realm (str):
        client_id (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, bool]):  Default: False.
        viewable_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ClientRepresentation']
     """


    return sync_detailed(
        realm=realm,
client=client,
client_id=client_id,
first=first,
max_=max_,
q=q,
search=search,
viewable_only=viewable_only,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_id: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, bool] = False,
    viewable_only: Union[Unset, bool] = False,

) -> Response[list['ClientRepresentation']]:
    """ Get clients belonging to the realm.

     If a client can’t be retrieved from the storage due to a problem with the underlying storage, it is
    silently removed from the returned list. This ensures that concurrent modifications to the list
    don’t prevent callers from retrieving this list.

    Args:
        realm (str):
        client_id (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, bool]):  Default: False.
        viewable_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ClientRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_id=client_id,
first=first,
max_=max_,
q=q,
search=search,
viewable_only=viewable_only,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_id: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, bool] = False,
    viewable_only: Union[Unset, bool] = False,

) -> list['ClientRepresentation'] | None:
    """ Get clients belonging to the realm.

     If a client can’t be retrieved from the storage due to a problem with the underlying storage, it is
    silently removed from the returned list. This ensures that concurrent modifications to the list
    don’t prevent callers from retrieving this list.

    Args:
        realm (str):
        client_id (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, bool]):  Default: False.
        viewable_only (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ClientRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
client_id=client_id,
first=first,
max_=max_,
q=q,
search=search,
viewable_only=viewable_only,

    )).parsed
