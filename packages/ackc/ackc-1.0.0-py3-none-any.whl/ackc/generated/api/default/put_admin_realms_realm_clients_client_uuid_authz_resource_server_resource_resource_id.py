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
    resource_id: str,
    *,
    body: ResourceRepresentation,
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
    headers: dict[str, Any] = {}


    

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
        "method": "put",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/resource/{resource_id}".format(realm=realm,client_uuid=client_uuid,resource_id=resource_id,),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Any | None:
    if response.status_code == 204:
        return None
    if response.status_code == 404:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_uuid: str,
    resource_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ResourceRepresentation,
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

) -> Response[Any]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        resource_id (str):
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
        body (ResourceRepresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
resource_id=resource_id,
body=body,
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


async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    resource_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ResourceRepresentation,
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

) -> Response[Any]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        resource_id (str):
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
        body (ResourceRepresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
resource_id=resource_id,
body=body,
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

