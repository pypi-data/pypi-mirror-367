from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.resource_representation import ResourceRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    field_id: Union[Unset, str] = UNSET,
    deep: Union[Unset, bool] = UNSET,
    exact_name: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    matching_uri: Union[Unset, bool] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    uri: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["_id"] = field_id

    params["deep"] = deep

    params["exactName"] = exact_name

    params["first"] = first

    params["matchingUri"] = matching_uri

    params["max"] = max_

    params["name"] = name

    params["owner"] = owner

    params["scope"] = scope

    params["type"] = type_

    params["uri"] = uri


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/resource".format(realm=realm,client_uuid=client_uuid,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['ResourceRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = ResourceRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['ResourceRepresentation']]:
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
    field_id: Union[Unset, str] = UNSET,
    deep: Union[Unset, bool] = UNSET,
    exact_name: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    matching_uri: Union[Unset, bool] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    uri: Union[Unset, str] = UNSET,

) -> Response[list['ResourceRepresentation']]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        field_id (Union[Unset, str]):
        deep (Union[Unset, bool]):
        exact_name (Union[Unset, bool]):
        first (Union[Unset, int]):
        matching_uri (Union[Unset, bool]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):
        uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ResourceRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
field_id=field_id,
deep=deep,
exact_name=exact_name,
first=first,
matching_uri=matching_uri,
max_=max_,
name=name,
owner=owner,
scope=scope,
type_=type_,
uri=uri,

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
    field_id: Union[Unset, str] = UNSET,
    deep: Union[Unset, bool] = UNSET,
    exact_name: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    matching_uri: Union[Unset, bool] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    uri: Union[Unset, str] = UNSET,

) -> list['ResourceRepresentation'] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        field_id (Union[Unset, str]):
        deep (Union[Unset, bool]):
        exact_name (Union[Unset, bool]):
        first (Union[Unset, int]):
        matching_uri (Union[Unset, bool]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):
        uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ResourceRepresentation']
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
field_id=field_id,
deep=deep,
exact_name=exact_name,
first=first,
matching_uri=matching_uri,
max_=max_,
name=name,
owner=owner,
scope=scope,
type_=type_,
uri=uri,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    field_id: Union[Unset, str] = UNSET,
    deep: Union[Unset, bool] = UNSET,
    exact_name: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    matching_uri: Union[Unset, bool] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    uri: Union[Unset, str] = UNSET,

) -> Response[list['ResourceRepresentation']]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        field_id (Union[Unset, str]):
        deep (Union[Unset, bool]):
        exact_name (Union[Unset, bool]):
        first (Union[Unset, int]):
        matching_uri (Union[Unset, bool]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):
        uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ResourceRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
field_id=field_id,
deep=deep,
exact_name=exact_name,
first=first,
matching_uri=matching_uri,
max_=max_,
name=name,
owner=owner,
scope=scope,
type_=type_,
uri=uri,

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
    field_id: Union[Unset, str] = UNSET,
    deep: Union[Unset, bool] = UNSET,
    exact_name: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    matching_uri: Union[Unset, bool] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    uri: Union[Unset, str] = UNSET,

) -> list['ResourceRepresentation'] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        field_id (Union[Unset, str]):
        deep (Union[Unset, bool]):
        exact_name (Union[Unset, bool]):
        first (Union[Unset, int]):
        matching_uri (Union[Unset, bool]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):
        uri (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ResourceRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
field_id=field_id,
deep=deep,
exact_name=exact_name,
first=first,
matching_uri=matching_uri,
max_=max_,
name=name,
owner=owner,
scope=scope,
type_=type_,
uri=uri,

    )).parsed
