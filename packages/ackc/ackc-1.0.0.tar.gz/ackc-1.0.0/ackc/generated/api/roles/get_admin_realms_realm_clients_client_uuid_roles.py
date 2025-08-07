from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.role_representation import RoleRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    brief_representation: Union[Unset, bool] = True,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = '',

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation

    params["first"] = first

    params["max"] = max_

    params["search"] = search


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/roles".format(realm=realm,client_uuid=client_uuid,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['RoleRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = RoleRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['RoleRepresentation']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = '',

) -> Response[Union[Any, list['RoleRepresentation']]]:
    """ Get all roles for the realm or client

    Args:
        realm (str):
        client_uuid (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        search (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['RoleRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
brief_representation=brief_representation,
first=first,
max_=max_,
search=search,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = '',

) -> Union[Any, list['RoleRepresentation']] | None:
    """ Get all roles for the realm or client

    Args:
        realm (str):
        client_uuid (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        search (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['RoleRepresentation']]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
brief_representation=brief_representation,
first=first,
max_=max_,
search=search,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = '',

) -> Response[Union[Any, list['RoleRepresentation']]]:
    """ Get all roles for the realm or client

    Args:
        realm (str):
        client_uuid (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        search (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['RoleRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
brief_representation=brief_representation,
first=first,
max_=max_,
search=search,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = '',

) -> Union[Any, list['RoleRepresentation']] | None:
    """ Get all roles for the realm or client

    Args:
        realm (str):
        client_uuid (str):
        brief_representation (Union[Unset, bool]):  Default: True.
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        search (Union[Unset, str]):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['RoleRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
brief_representation=brief_representation,
first=first,
max_=max_,
search=search,

    )).parsed
