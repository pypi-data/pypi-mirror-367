from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.group_representation import GroupRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    group_id: str,
    *,
    brief_representation: Union[Unset, bool] = False,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation

    params["exact"] = exact

    params["first"] = first

    params["max"] = max_

    params["search"] = search

    params["subGroupsCount"] = sub_groups_count


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/groups/{group_id}/children".format(realm=realm,group_id=group_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['GroupRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = GroupRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['GroupRepresentation']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> Response[list['GroupRepresentation']]:
    """ Return a paginated list of subgroups that have a parent group corresponding to the group on the URL

    Args:
        realm (str):
        group_id (str):
        brief_representation (Union[Unset, bool]):  Default: False.
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        search (Union[Unset, str]):
        sub_groups_count (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GroupRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
group_id=group_id,
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
search=search,
sub_groups_count=sub_groups_count,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> list['GroupRepresentation'] | None:
    """ Return a paginated list of subgroups that have a parent group corresponding to the group on the URL

    Args:
        realm (str):
        group_id (str):
        brief_representation (Union[Unset, bool]):  Default: False.
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        search (Union[Unset, str]):
        sub_groups_count (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GroupRepresentation']
     """


    return sync_detailed(
        realm=realm,
group_id=group_id,
client=client,
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
search=search,
sub_groups_count=sub_groups_count,

    ).parsed

async def asyncio_detailed(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> Response[list['GroupRepresentation']]:
    """ Return a paginated list of subgroups that have a parent group corresponding to the group on the URL

    Args:
        realm (str):
        group_id (str):
        brief_representation (Union[Unset, bool]):  Default: False.
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        search (Union[Unset, str]):
        sub_groups_count (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GroupRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
group_id=group_id,
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
search=search,
sub_groups_count=sub_groups_count,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = False,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> list['GroupRepresentation'] | None:
    """ Return a paginated list of subgroups that have a parent group corresponding to the group on the URL

    Args:
        realm (str):
        group_id (str):
        brief_representation (Union[Unset, bool]):  Default: False.
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        search (Union[Unset, str]):
        sub_groups_count (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GroupRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
group_id=group_id,
client=client,
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
search=search,
sub_groups_count=sub_groups_count,

    )).parsed
