from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...types import UNSET, Unset
from typing import Union



def _get_kwargs(
    realm: str,
    user_id: str,
    *,
    client_id: Union[Unset, str] = UNSET,
    redirect_uri: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["client_id"] = client_id

    params["redirect_uri"] = redirect_uri


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/realms/{realm}/users/{user_id}/reset-password-email".format(realm=realm,user_id=user_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Any | None:
    if response.status_code == 204:
        return None
    if response.status_code == 400:
        return None
    if response.status_code == 403:
        return None
    if response.status_code == 404:
        return None
    if response.status_code == 500:
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
    *,
    client: Union[AuthenticatedClient, Client],
    client_id: Union[Unset, str] = UNSET,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Response[Any]:
    """ Send an email to the user with a link they can click to reset their password.

     The redirectUri and clientId parameters are optional. The default for the redirect is the account
    client. This endpoint has been deprecated.  Please use the execute-actions-email passing a list with
    UPDATE_PASSWORD within it.

    Args:
        realm (str):
        user_id (str):
        client_id (Union[Unset, str]):
        redirect_uri (Union[Unset, str]):

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
redirect_uri=redirect_uri,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    realm: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    client_id: Union[Unset, str] = UNSET,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Response[Any]:
    """ Send an email to the user with a link they can click to reset their password.

     The redirectUri and clientId parameters are optional. The default for the redirect is the account
    client. This endpoint has been deprecated.  Please use the execute-actions-email passing a list with
    UPDATE_PASSWORD within it.

    Args:
        realm (str):
        user_id (str):
        client_id (Union[Unset, str]):
        redirect_uri (Union[Unset, str]):

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
redirect_uri=redirect_uri,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

