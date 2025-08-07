from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.realm_representation import RealmRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    brief_representation: Union[Unset, bool] = False,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms",
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['RealmRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = RealmRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['RealmRepresentation']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,

) -> Response[Union[Any, list['RealmRepresentation']]]:
    """ Get accessible realms Returns a list of accessible realms. The list is filtered based on what realms
    the caller is allowed to view.

    Args:
        brief_representation (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['RealmRepresentation']]]
     """


    kwargs = _get_kwargs(
        brief_representation=brief_representation,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,

) -> Union[Any, list['RealmRepresentation']] | None:
    """ Get accessible realms Returns a list of accessible realms. The list is filtered based on what realms
    the caller is allowed to view.

    Args:
        brief_representation (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['RealmRepresentation']]
     """


    return sync_detailed(
        client=client,
brief_representation=brief_representation,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,

) -> Response[Union[Any, list['RealmRepresentation']]]:
    """ Get accessible realms Returns a list of accessible realms. The list is filtered based on what realms
    the caller is allowed to view.

    Args:
        brief_representation (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['RealmRepresentation']]]
     """


    kwargs = _get_kwargs(
        brief_representation=brief_representation,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,

) -> Union[Any, list['RealmRepresentation']] | None:
    """ Get accessible realms Returns a list of accessible realms. The list is filtered based on what realms
    the caller is allowed to view.

    Args:
        brief_representation (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['RealmRepresentation']]
     """


    return (await asyncio_detailed(
        client=client,
brief_representation=brief_representation,

    )).parsed
