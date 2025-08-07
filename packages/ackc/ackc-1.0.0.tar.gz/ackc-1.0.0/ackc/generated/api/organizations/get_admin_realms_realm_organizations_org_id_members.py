from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.member_representation import MemberRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    org_id: str,
    *,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    membership_type: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["exact"] = exact

    params["first"] = first

    params["max"] = max_

    params["membershipType"] = membership_type

    params["search"] = search


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/organizations/{org_id}/members".format(realm=realm,org_id=org_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['MemberRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = MemberRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['MemberRepresentation']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    org_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    membership_type: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> Response[list['MemberRepresentation']]:
    """ Returns a paginated list of organization members filtered according to the specified parameters

    Args:
        realm (str):
        org_id (str):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        membership_type (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MemberRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
org_id=org_id,
exact=exact,
first=first,
max_=max_,
membership_type=membership_type,
search=search,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    org_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    membership_type: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> list['MemberRepresentation'] | None:
    """ Returns a paginated list of organization members filtered according to the specified parameters

    Args:
        realm (str):
        org_id (str):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        membership_type (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MemberRepresentation']
     """


    return sync_detailed(
        realm=realm,
org_id=org_id,
client=client,
exact=exact,
first=first,
max_=max_,
membership_type=membership_type,
search=search,

    ).parsed

async def asyncio_detailed(
    realm: str,
    org_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    membership_type: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> Response[list['MemberRepresentation']]:
    """ Returns a paginated list of organization members filtered according to the specified parameters

    Args:
        realm (str):
        org_id (str):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        membership_type (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MemberRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
org_id=org_id,
exact=exact,
first=first,
max_=max_,
membership_type=membership_type,
search=search,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    org_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = 0,
    max_: Union[Unset, int] = 10,
    membership_type: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> list['MemberRepresentation'] | None:
    """ Returns a paginated list of organization members filtered according to the specified parameters

    Args:
        realm (str):
        org_id (str):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):  Default: 0.
        max_ (Union[Unset, int]):  Default: 10.
        membership_type (Union[Unset, str]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MemberRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
org_id=org_id,
client=client,
exact=exact,
first=first,
max_=max_,
membership_type=membership_type,
search=search,

    )).parsed
