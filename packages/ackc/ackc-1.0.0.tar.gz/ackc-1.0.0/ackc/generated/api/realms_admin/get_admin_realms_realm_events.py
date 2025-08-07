from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.event_representation import EventRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    client_query: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    ip_address: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    user: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["client"] = client_query

    params["dateFrom"] = date_from

    params["dateTo"] = date_to

    params["direction"] = direction

    params["first"] = first

    params["ipAddress"] = ip_address

    params["max"] = max_

    json_type_: Union[Unset, list[str]] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_


    params["type"] = json_type_

    params["user"] = user


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/events".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['EventRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = EventRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['EventRepresentation']]]:
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
    client_query: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    ip_address: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    user: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['EventRepresentation']]]:
    """ Get events Returns all events, or filters them based on URL query parameters listed here

    Args:
        realm (str):
        client_query (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        ip_address (Union[Unset, str]):
        max_ (Union[Unset, int]):
        type_ (Union[Unset, list[str]]):
        user (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['EventRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_query=client_query,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
ip_address=ip_address,
max_=max_,
type_=type_,
user=user,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_query: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    ip_address: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    user: Union[Unset, str] = UNSET,

) -> Union[Any, list['EventRepresentation']] | None:
    """ Get events Returns all events, or filters them based on URL query parameters listed here

    Args:
        realm (str):
        client_query (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        ip_address (Union[Unset, str]):
        max_ (Union[Unset, int]):
        type_ (Union[Unset, list[str]]):
        user (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['EventRepresentation']]
     """


    return sync_detailed(
        realm=realm,
client=client,
client_query=client_query,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
ip_address=ip_address,
max_=max_,
type_=type_,
user=user,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_query: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    ip_address: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    user: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['EventRepresentation']]]:
    """ Get events Returns all events, or filters them based on URL query parameters listed here

    Args:
        realm (str):
        client_query (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        ip_address (Union[Unset, str]):
        max_ (Union[Unset, int]):
        type_ (Union[Unset, list[str]]):
        user (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['EventRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_query=client_query,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
ip_address=ip_address,
max_=max_,
type_=type_,
user=user,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_query: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    ip_address: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    user: Union[Unset, str] = UNSET,

) -> Union[Any, list['EventRepresentation']] | None:
    """ Get events Returns all events, or filters them based on URL query parameters listed here

    Args:
        realm (str):
        client_query (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        ip_address (Union[Unset, str]):
        max_ (Union[Unset, int]):
        type_ (Union[Unset, list[str]]):
        user (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['EventRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
client_query=client_query,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
ip_address=ip_address,
max_=max_,
type_=type_,
user=user,

    )).parsed
