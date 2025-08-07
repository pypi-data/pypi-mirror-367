from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import cast



def _get_kwargs(
    realm: str,
    user_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/users/{user_id}/configured-user-storage-credential-types".format(realm=realm,user_id=user_id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list[str]] | None:
    if response.status_code == 200:
        response_200 = cast(list[str], response.json())

        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list[str]]]:
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

) -> Response[Union[Any, list[str]]]:
    r""" Return credential types, which are provided by the user storage where user is stored.

     Returned values can contain for example \"password\", \"otp\" etc. This will always return empty
    list for \"local\" users, which are not backed by any user storage

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list[str]]]
     """


    kwargs = _get_kwargs(
        realm=realm,
user_id=user_id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, list[str]] | None:
    r""" Return credential types, which are provided by the user storage where user is stored.

     Returned values can contain for example \"password\", \"otp\" etc. This will always return empty
    list for \"local\" users, which are not backed by any user storage

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list[str]]
     """


    return sync_detailed(
        realm=realm,
user_id=user_id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, list[str]]]:
    r""" Return credential types, which are provided by the user storage where user is stored.

     Returned values can contain for example \"password\", \"otp\" etc. This will always return empty
    list for \"local\" users, which are not backed by any user storage

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list[str]]]
     """


    kwargs = _get_kwargs(
        realm=realm,
user_id=user_id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    user_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, list[str]] | None:
    r""" Return credential types, which are provided by the user storage where user is stored.

     Returned values can contain for example \"password\", \"otp\" etc. This will always return empty
    list for \"local\" users, which are not backed by any user storage

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list[str]]
     """


    return (await asyncio_detailed(
        realm=realm,
user_id=user_id,
client=client,

    )).parsed
