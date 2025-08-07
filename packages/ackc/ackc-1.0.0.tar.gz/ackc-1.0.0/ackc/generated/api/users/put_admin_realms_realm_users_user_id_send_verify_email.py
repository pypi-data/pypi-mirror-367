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
    lifespan: Union[Unset, int] = UNSET,
    redirect_uri: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["client_id"] = client_id

    params["lifespan"] = lifespan

    params["redirect_uri"] = redirect_uri


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/realms/{realm}/users/{user_id}/send-verify-email".format(realm=realm,user_id=user_id,),
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
    lifespan: Union[Unset, int] = UNSET,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Response[Any]:
    """ Send an email-verification email to the user An email contains a link the user can click to verify
    their email address.

     The redirectUri, clientId and lifespan parameters are optional. The default for the redirect is the
    account client. The default for the lifespan is 12 hours

    Args:
        realm (str):
        user_id (str):
        client_id (Union[Unset, str]):
        lifespan (Union[Unset, int]):
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
lifespan=lifespan,
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
    lifespan: Union[Unset, int] = UNSET,
    redirect_uri: Union[Unset, str] = UNSET,

) -> Response[Any]:
    """ Send an email-verification email to the user An email contains a link the user can click to verify
    their email address.

     The redirectUri, clientId and lifespan parameters are optional. The default for the redirect is the
    account client. The default for the lifespan is 12 hours

    Args:
        realm (str):
        user_id (str):
        client_id (Union[Unset, str]):
        lifespan (Union[Unset, int]):
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
lifespan=lifespan,
redirect_uri=redirect_uri,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

