from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.client_profiles_representation import ClientProfilesRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    include_global_profiles: Union[Unset, bool] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["include-global-profiles"] = include_global_profiles


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/client-policies/profiles".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ClientProfilesRepresentation | None:
    if response.status_code == 200:
        response_200 = ClientProfilesRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ClientProfilesRepresentation]:
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
    include_global_profiles: Union[Unset, bool] = UNSET,

) -> Response[ClientProfilesRepresentation]:
    """ 
    Args:
        realm (str):
        include_global_profiles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientProfilesRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
include_global_profiles=include_global_profiles,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_global_profiles: Union[Unset, bool] = UNSET,

) -> ClientProfilesRepresentation | None:
    """ 
    Args:
        realm (str):
        include_global_profiles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientProfilesRepresentation
     """


    return sync_detailed(
        realm=realm,
client=client,
include_global_profiles=include_global_profiles,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_global_profiles: Union[Unset, bool] = UNSET,

) -> Response[ClientProfilesRepresentation]:
    """ 
    Args:
        realm (str):
        include_global_profiles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientProfilesRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
include_global_profiles=include_global_profiles,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_global_profiles: Union[Unset, bool] = UNSET,

) -> ClientProfilesRepresentation | None:
    """ 
    Args:
        realm (str):
        include_global_profiles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientProfilesRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
include_global_profiles=include_global_profiles,

    )).parsed
