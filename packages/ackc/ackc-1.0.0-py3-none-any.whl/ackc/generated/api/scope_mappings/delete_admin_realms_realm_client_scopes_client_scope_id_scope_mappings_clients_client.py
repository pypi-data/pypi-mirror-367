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
    client_scope_id: str,
    client_path: str,
    *,
    body: list['RoleRepresentation'],

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/admin/realms/{realm}/client-scopes/{client_scope_id}/scope-mappings/clients/{client_path}".format(realm=realm,client_scope_id=client_scope_id,client_path=client_path,),
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
    client_scope_id: str,
    client_path: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list['RoleRepresentation'],

) -> Response[Any]:
    """ Remove client-level roles from the client's scope.

    Args:
        realm (str):
        client_scope_id (str):
        client_path (str):
        body (list['RoleRepresentation']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_scope_id=client_scope_id,
client_path=client_path,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    realm: str,
    client_scope_id: str,
    client_path: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: list['RoleRepresentation'],

) -> Response[Any]:
    """ Remove client-level roles from the client's scope.

    Args:
        realm (str):
        client_scope_id (str):
        client_path (str):
        body (list['RoleRepresentation']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_scope_id=client_scope_id,
client_path=client_path,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

