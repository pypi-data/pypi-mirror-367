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
    *,
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["email"] = email

    params["emailVerified"] = email_verified

    params["enabled"] = enabled

    params["firstName"] = first_name

    params["lastName"] = last_name

    params["q"] = q

    params["search"] = search

    params["username"] = username


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/users/count".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, int] | None:
    if response.status_code == 200:
        response_200 = cast(int, response.json())
        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, int]]:
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
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Response[Union[Any, int]]:
    """ Returns the number of users that match the given criteria.

     It can be called in three different ways. 1. Don’t specify any criteria and pass {@code null}. The
    number of all users within that realm will be returned. <p> 2. If {@code search} is specified other
    criteria such as {@code last} will be ignored even though you set them. The {@code search} string
    will be matched against the first and last name, the username and the email of a user. <p> 3. If
    {@code search} is unspecified but any of {@code last}, {@code first}, {@code email} or {@code
    username} those criteria are matched against their respective fields on a user entity. Combined with
    a logical and.

    Args:
        realm (str):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, int]]
     """


    kwargs = _get_kwargs(
        realm=realm,
email=email,
email_verified=email_verified,
enabled=enabled,
first_name=first_name,
last_name=last_name,
q=q,
search=search,
username=username,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Union[Any, int] | None:
    """ Returns the number of users that match the given criteria.

     It can be called in three different ways. 1. Don’t specify any criteria and pass {@code null}. The
    number of all users within that realm will be returned. <p> 2. If {@code search} is specified other
    criteria such as {@code last} will be ignored even though you set them. The {@code search} string
    will be matched against the first and last name, the username and the email of a user. <p> 3. If
    {@code search} is unspecified but any of {@code last}, {@code first}, {@code email} or {@code
    username} those criteria are matched against their respective fields on a user entity. Combined with
    a logical and.

    Args:
        realm (str):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, int]
     """


    return sync_detailed(
        realm=realm,
client=client,
email=email,
email_verified=email_verified,
enabled=enabled,
first_name=first_name,
last_name=last_name,
q=q,
search=search,
username=username,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Response[Union[Any, int]]:
    """ Returns the number of users that match the given criteria.

     It can be called in three different ways. 1. Don’t specify any criteria and pass {@code null}. The
    number of all users within that realm will be returned. <p> 2. If {@code search} is specified other
    criteria such as {@code last} will be ignored even though you set them. The {@code search} string
    will be matched against the first and last name, the username and the email of a user. <p> 3. If
    {@code search} is unspecified but any of {@code last}, {@code first}, {@code email} or {@code
    username} those criteria are matched against their respective fields on a user entity. Combined with
    a logical and.

    Args:
        realm (str):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, int]]
     """


    kwargs = _get_kwargs(
        realm=realm,
email=email,
email_verified=email_verified,
enabled=enabled,
first_name=first_name,
last_name=last_name,
q=q,
search=search,
username=username,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Union[Any, int] | None:
    """ Returns the number of users that match the given criteria.

     It can be called in three different ways. 1. Don’t specify any criteria and pass {@code null}. The
    number of all users within that realm will be returned. <p> 2. If {@code search} is specified other
    criteria such as {@code last} will be ignored even though you set them. The {@code search} string
    will be matched against the first and last name, the username and the email of a user. <p> 3. If
    {@code search} is unspecified but any of {@code last}, {@code first}, {@code email} or {@code
    username} those criteria are matched against their respective fields on a user entity. Combined with
    a logical and.

    Args:
        realm (str):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, int]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
email=email,
email_verified=email_verified,
enabled=enabled,
first_name=first_name,
last_name=last_name,
q=q,
search=search,
username=username,

    )).parsed
