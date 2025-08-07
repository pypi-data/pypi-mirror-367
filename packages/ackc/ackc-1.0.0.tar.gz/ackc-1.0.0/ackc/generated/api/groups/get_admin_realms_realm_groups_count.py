from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_groups_count_response_200 import GetAdminRealmsRealmGroupsCountResponse200
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    search: Union[Unset, str] = UNSET,
    top: Union[Unset, bool] = False,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["search"] = search

    params["top"] = top


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/groups/count".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> GetAdminRealmsRealmGroupsCountResponse200 | None:
    if response.status_code == 200:
        response_200 = GetAdminRealmsRealmGroupsCountResponse200.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[GetAdminRealmsRealmGroupsCountResponse200]:
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
    search: Union[Unset, str] = UNSET,
    top: Union[Unset, bool] = False,

) -> Response[GetAdminRealmsRealmGroupsCountResponse200]:
    """ Returns the groups counts.

    Args:
        realm (str):
        search (Union[Unset, str]):
        top (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminRealmsRealmGroupsCountResponse200]
     """


    kwargs = _get_kwargs(
        realm=realm,
search=search,
top=top,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    search: Union[Unset, str] = UNSET,
    top: Union[Unset, bool] = False,

) -> GetAdminRealmsRealmGroupsCountResponse200 | None:
    """ Returns the groups counts.

    Args:
        realm (str):
        search (Union[Unset, str]):
        top (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminRealmsRealmGroupsCountResponse200
     """


    return sync_detailed(
        realm=realm,
client=client,
search=search,
top=top,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    search: Union[Unset, str] = UNSET,
    top: Union[Unset, bool] = False,

) -> Response[GetAdminRealmsRealmGroupsCountResponse200]:
    """ Returns the groups counts.

    Args:
        realm (str):
        search (Union[Unset, str]):
        top (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAdminRealmsRealmGroupsCountResponse200]
     """


    kwargs = _get_kwargs(
        realm=realm,
search=search,
top=top,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    search: Union[Unset, str] = UNSET,
    top: Union[Unset, bool] = False,

) -> GetAdminRealmsRealmGroupsCountResponse200 | None:
    """ Returns the groups counts.

    Args:
        realm (str):
        search (Union[Unset, str]):
        top (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAdminRealmsRealmGroupsCountResponse200
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
search=search,
top=top,

    )).parsed
