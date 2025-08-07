from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.scope_representation import ScopeRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    name: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["name"] = name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/scope/search".format(realm=realm,client_uuid=client_uuid,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['ScopeRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = ScopeRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['ScopeRepresentation']]]:
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
    name: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['ScopeRepresentation']]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['ScopeRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
name=name,

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
    name: Union[Unset, str] = UNSET,

) -> Union[Any, list['ScopeRepresentation']] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['ScopeRepresentation']]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
name=name,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['ScopeRepresentation']]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['ScopeRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
name=name,

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
    name: Union[Unset, str] = UNSET,

) -> Union[Any, list['ScopeRepresentation']] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['ScopeRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
name=name,

    )).parsed
