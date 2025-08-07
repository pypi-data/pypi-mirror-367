from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.component_representation import ComponentRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    name: Union[Unset, str] = UNSET,
    parent: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["name"] = name

    params["parent"] = parent

    params["type"] = type_


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/components".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['ComponentRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = ComponentRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['ComponentRepresentation']]:
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
    name: Union[Unset, str] = UNSET,
    parent: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> Response[list['ComponentRepresentation']]:
    """ 
    Args:
        realm (str):
        name (Union[Unset, str]):
        parent (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ComponentRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
name=name,
parent=parent,
type_=type_,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = UNSET,
    parent: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> list['ComponentRepresentation'] | None:
    """ 
    Args:
        realm (str):
        name (Union[Unset, str]):
        parent (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ComponentRepresentation']
     """


    return sync_detailed(
        realm=realm,
client=client,
name=name,
parent=parent,
type_=type_,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = UNSET,
    parent: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> Response[list['ComponentRepresentation']]:
    """ 
    Args:
        realm (str):
        name (Union[Unset, str]):
        parent (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ComponentRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
name=name,
parent=parent,
type_=type_,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    name: Union[Unset, str] = UNSET,
    parent: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> list['ComponentRepresentation'] | None:
    """ 
    Args:
        realm (str):
        name (Union[Unset, str]):
        parent (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ComponentRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
name=name,
parent=parent,
type_=type_,

    )).parsed
