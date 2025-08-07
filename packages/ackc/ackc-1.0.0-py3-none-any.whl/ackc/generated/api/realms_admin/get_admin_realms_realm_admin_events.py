from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.admin_event_representation import AdminEventRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    auth_client: Union[Unset, str] = UNSET,
    auth_ip_address: Union[Unset, str] = UNSET,
    auth_realm: Union[Unset, str] = UNSET,
    auth_user: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    operation_types: Union[Unset, list[str]] = UNSET,
    resource_path: Union[Unset, str] = UNSET,
    resource_types: Union[Unset, list[str]] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["authClient"] = auth_client

    params["authIpAddress"] = auth_ip_address

    params["authRealm"] = auth_realm

    params["authUser"] = auth_user

    params["dateFrom"] = date_from

    params["dateTo"] = date_to

    params["direction"] = direction

    params["first"] = first

    params["max"] = max_

    json_operation_types: Union[Unset, list[str]] = UNSET
    if not isinstance(operation_types, Unset):
        json_operation_types = operation_types


    params["operationTypes"] = json_operation_types

    params["resourcePath"] = resource_path

    json_resource_types: Union[Unset, list[str]] = UNSET
    if not isinstance(resource_types, Unset):
        json_resource_types = resource_types


    params["resourceTypes"] = json_resource_types


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/admin-events".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['AdminEventRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = AdminEventRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['AdminEventRepresentation']]]:
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
    auth_client: Union[Unset, str] = UNSET,
    auth_ip_address: Union[Unset, str] = UNSET,
    auth_realm: Union[Unset, str] = UNSET,
    auth_user: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    operation_types: Union[Unset, list[str]] = UNSET,
    resource_path: Union[Unset, str] = UNSET,
    resource_types: Union[Unset, list[str]] = UNSET,

) -> Response[Union[Any, list['AdminEventRepresentation']]]:
    """ Get admin events Returns all admin events, or filters events based on URL query parameters listed
    here

    Args:
        realm (str):
        auth_client (Union[Unset, str]):
        auth_ip_address (Union[Unset, str]):
        auth_realm (Union[Unset, str]):
        auth_user (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        operation_types (Union[Unset, list[str]]):
        resource_path (Union[Unset, str]):
        resource_types (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['AdminEventRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
auth_client=auth_client,
auth_ip_address=auth_ip_address,
auth_realm=auth_realm,
auth_user=auth_user,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
max_=max_,
operation_types=operation_types,
resource_path=resource_path,
resource_types=resource_types,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    auth_client: Union[Unset, str] = UNSET,
    auth_ip_address: Union[Unset, str] = UNSET,
    auth_realm: Union[Unset, str] = UNSET,
    auth_user: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    operation_types: Union[Unset, list[str]] = UNSET,
    resource_path: Union[Unset, str] = UNSET,
    resource_types: Union[Unset, list[str]] = UNSET,

) -> Union[Any, list['AdminEventRepresentation']] | None:
    """ Get admin events Returns all admin events, or filters events based on URL query parameters listed
    here

    Args:
        realm (str):
        auth_client (Union[Unset, str]):
        auth_ip_address (Union[Unset, str]):
        auth_realm (Union[Unset, str]):
        auth_user (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        operation_types (Union[Unset, list[str]]):
        resource_path (Union[Unset, str]):
        resource_types (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['AdminEventRepresentation']]
     """


    return sync_detailed(
        realm=realm,
client=client,
auth_client=auth_client,
auth_ip_address=auth_ip_address,
auth_realm=auth_realm,
auth_user=auth_user,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
max_=max_,
operation_types=operation_types,
resource_path=resource_path,
resource_types=resource_types,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    auth_client: Union[Unset, str] = UNSET,
    auth_ip_address: Union[Unset, str] = UNSET,
    auth_realm: Union[Unset, str] = UNSET,
    auth_user: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    operation_types: Union[Unset, list[str]] = UNSET,
    resource_path: Union[Unset, str] = UNSET,
    resource_types: Union[Unset, list[str]] = UNSET,

) -> Response[Union[Any, list['AdminEventRepresentation']]]:
    """ Get admin events Returns all admin events, or filters events based on URL query parameters listed
    here

    Args:
        realm (str):
        auth_client (Union[Unset, str]):
        auth_ip_address (Union[Unset, str]):
        auth_realm (Union[Unset, str]):
        auth_user (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        operation_types (Union[Unset, list[str]]):
        resource_path (Union[Unset, str]):
        resource_types (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['AdminEventRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
auth_client=auth_client,
auth_ip_address=auth_ip_address,
auth_realm=auth_realm,
auth_user=auth_user,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
max_=max_,
operation_types=operation_types,
resource_path=resource_path,
resource_types=resource_types,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    auth_client: Union[Unset, str] = UNSET,
    auth_ip_address: Union[Unset, str] = UNSET,
    auth_realm: Union[Unset, str] = UNSET,
    auth_user: Union[Unset, str] = UNSET,
    date_from: Union[Unset, str] = UNSET,
    date_to: Union[Unset, str] = UNSET,
    direction: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    operation_types: Union[Unset, list[str]] = UNSET,
    resource_path: Union[Unset, str] = UNSET,
    resource_types: Union[Unset, list[str]] = UNSET,

) -> Union[Any, list['AdminEventRepresentation']] | None:
    """ Get admin events Returns all admin events, or filters events based on URL query parameters listed
    here

    Args:
        realm (str):
        auth_client (Union[Unset, str]):
        auth_ip_address (Union[Unset, str]):
        auth_realm (Union[Unset, str]):
        auth_user (Union[Unset, str]):
        date_from (Union[Unset, str]):
        date_to (Union[Unset, str]):
        direction (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        operation_types (Union[Unset, list[str]]):
        resource_path (Union[Unset, str]):
        resource_types (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['AdminEventRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
auth_client=auth_client,
auth_ip_address=auth_ip_address,
auth_realm=auth_realm,
auth_user=auth_user,
date_from=date_from,
date_to=date_to,
direction=direction,
first=first,
max_=max_,
operation_types=operation_types,
resource_path=resource_path,
resource_types=resource_types,

    )).parsed
