from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.identity_provider_representation import IdentityProviderRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    brief_representation: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    realm_only: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation

    params["first"] = first

    params["max"] = max_

    params["realmOnly"] = realm_only

    params["search"] = search


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/identity-provider/instances".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['IdentityProviderRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = IdentityProviderRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['IdentityProviderRepresentation']]:
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
    brief_representation: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    realm_only: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> Response[list['IdentityProviderRepresentation']]:
    """ List identity providers

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        realm_only (Union[Unset, bool]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['IdentityProviderRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
brief_representation=brief_representation,
first=first,
max_=max_,
realm_only=realm_only,
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
    brief_representation: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    realm_only: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> list['IdentityProviderRepresentation'] | None:
    """ List identity providers

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        realm_only (Union[Unset, bool]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['IdentityProviderRepresentation']
     """


    return sync_detailed(
        realm=realm,
client=client,
brief_representation=brief_representation,
first=first,
max_=max_,
realm_only=realm_only,
search=search,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    realm_only: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> Response[list['IdentityProviderRepresentation']]:
    """ List identity providers

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        realm_only (Union[Unset, bool]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['IdentityProviderRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
brief_representation=brief_representation,
first=first,
max_=max_,
realm_only=realm_only,
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
    brief_representation: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    realm_only: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,

) -> list['IdentityProviderRepresentation'] | None:
    """ List identity providers

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        realm_only (Union[Unset, bool]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['IdentityProviderRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
brief_representation=brief_representation,
first=first,
max_=max_,
realm_only=realm_only,
search=search,

    )).parsed
