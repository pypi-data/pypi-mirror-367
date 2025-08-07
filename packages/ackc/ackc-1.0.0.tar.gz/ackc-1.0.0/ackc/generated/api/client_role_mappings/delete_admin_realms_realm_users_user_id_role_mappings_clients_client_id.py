from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.role_representation import RoleRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    user_id: str,
    client_id: str,
    *,
    body: list['RoleRepresentation'],

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_id}".format(realm=realm,user_id=user_id,client_id=client_id,),
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)





    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Any | None:
    if response.status_code == 204:
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
    user_id: str,
    client_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list['RoleRepresentation'],

) -> Response[Any]:
    """ Delete client-level roles from user or group role mapping

    Args:
        realm (str):
        user_id (str):
        client_id (str):
        body (list['RoleRepresentation']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
user_id=user_id,
client_id=client_id,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    realm: str,
    user_id: str,
    client_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list['RoleRepresentation'],

) -> Response[Any]:
    """ Delete client-level roles from user or group role mapping

    Args:
        realm (str):
        user_id (str):
        client_id (str):
        body (list['RoleRepresentation']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
user_id=user_id,
client_id=client_id,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

