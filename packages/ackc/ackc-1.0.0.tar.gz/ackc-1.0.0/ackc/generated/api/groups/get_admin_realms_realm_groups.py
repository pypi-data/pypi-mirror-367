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
    *,
    brief_representation: Union[Unset, bool] = True,
    exact: Union[Unset, bool] = False,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    populate_hierarchy: Union[Unset, bool] = True,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation

    params["exact"] = exact

    params["first"] = first

    params["max"] = max_

    params["populateHierarchy"] = populate_hierarchy

    params["q"] = q

    params["search"] = search

    params["subGroupsCount"] = sub_groups_count


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/groups".format(realm=realm,),
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
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    exact: Union[Unset, bool] = False,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    populate_hierarchy: Union[Unset, bool] = True,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> Response[list['GroupRepresentation']]:
    """ Get group hierarchy.  Only `name` and `id` are returned.  `subGroups` are only returned when using
    the `search` or `q` parameter. If none of these parameters is provided, the top-level groups are
    returned without `subGroups` being filled.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        exact (Union[Unset, bool]):  Default: False.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        populate_hierarchy (Union[Unset, bool]):  Default: True.
        q (Union[Unset, str]):
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
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
populate_hierarchy=populate_hierarchy,
q=q,
search=search,
sub_groups_count=sub_groups_count,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    exact: Union[Unset, bool] = False,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    populate_hierarchy: Union[Unset, bool] = True,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> list['GroupRepresentation'] | None:
    """ Get group hierarchy.  Only `name` and `id` are returned.  `subGroups` are only returned when using
    the `search` or `q` parameter. If none of these parameters is provided, the top-level groups are
    returned without `subGroups` being filled.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        exact (Union[Unset, bool]):  Default: False.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        populate_hierarchy (Union[Unset, bool]):  Default: True.
        q (Union[Unset, str]):
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
client=client,
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
populate_hierarchy=populate_hierarchy,
q=q,
search=search,
sub_groups_count=sub_groups_count,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    exact: Union[Unset, bool] = False,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    populate_hierarchy: Union[Unset, bool] = True,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> Response[list['GroupRepresentation']]:
    """ Get group hierarchy.  Only `name` and `id` are returned.  `subGroups` are only returned when using
    the `search` or `q` parameter. If none of these parameters is provided, the top-level groups are
    returned without `subGroups` being filled.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        exact (Union[Unset, bool]):  Default: False.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        populate_hierarchy (Union[Unset, bool]):  Default: True.
        q (Union[Unset, str]):
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
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
populate_hierarchy=populate_hierarchy,
q=q,
search=search,
sub_groups_count=sub_groups_count,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    exact: Union[Unset, bool] = False,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    populate_hierarchy: Union[Unset, bool] = True,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    sub_groups_count: Union[Unset, bool] = True,

) -> list['GroupRepresentation'] | None:
    """ Get group hierarchy.  Only `name` and `id` are returned.  `subGroups` are only returned when using
    the `search` or `q` parameter. If none of these parameters is provided, the top-level groups are
    returned without `subGroups` being filled.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        exact (Union[Unset, bool]):  Default: False.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        populate_hierarchy (Union[Unset, bool]):  Default: True.
        q (Union[Unset, str]):
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
client=client,
brief_representation=brief_representation,
exact=exact,
first=first,
max_=max_,
populate_hierarchy=populate_hierarchy,
q=q,
search=search,
sub_groups_count=sub_groups_count,

    )).parsed
