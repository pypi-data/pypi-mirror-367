from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.management_permission_reference import ManagementPermissionReference
from typing import cast



def _get_kwargs(
    realm: str,
    group_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/groups/{group_id}/management/permissions".format(realm=realm,group_id=group_id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ManagementPermissionReference | None:
    if response.status_code == 200:
        response_200 = ManagementPermissionReference.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ManagementPermissionReference]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ManagementPermissionReference]:
    """ Return object stating whether client Authorization permissions have been initialized or not and a
    reference

    Args:
        realm (str):
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ManagementPermissionReference]
     """


    kwargs = _get_kwargs(
        realm=realm,
group_id=group_id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> ManagementPermissionReference | None:
    """ Return object stating whether client Authorization permissions have been initialized or not and a
    reference

    Args:
        realm (str):
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ManagementPermissionReference
     """


    return sync_detailed(
        realm=realm,
group_id=group_id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[ManagementPermissionReference]:
    """ Return object stating whether client Authorization permissions have been initialized or not and a
    reference

    Args:
        realm (str):
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ManagementPermissionReference]
     """


    kwargs = _get_kwargs(
        realm=realm,
group_id=group_id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    group_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> ManagementPermissionReference | None:
    """ Return object stating whether client Authorization permissions have been initialized or not and a
    reference

    Args:
        realm (str):
        group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ManagementPermissionReference
     """


    return (await asyncio_detailed(
        realm=realm,
group_id=group_id,
client=client,

    )).parsed
