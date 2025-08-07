from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.user_representation import UserRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    brief_representation: Union[Unset, bool] = UNSET,
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    idp_alias: Union[Unset, str] = UNSET,
    idp_user_id: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation

    params["email"] = email

    params["emailVerified"] = email_verified

    params["enabled"] = enabled

    params["exact"] = exact

    params["first"] = first

    params["firstName"] = first_name

    params["idpAlias"] = idp_alias

    params["idpUserId"] = idp_user_id

    params["lastName"] = last_name

    params["max"] = max_

    params["q"] = q

    params["search"] = search

    params["username"] = username


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/users".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['UserRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = UserRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['UserRepresentation']]]:
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
    brief_representation: Union[Unset, bool] = UNSET,
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    idp_alias: Union[Unset, str] = UNSET,
    idp_user_id: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['UserRepresentation']]]:
    """ Get users Returns a stream of users, filtered according to query parameters.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):
        first_name (Union[Unset, str]):
        idp_alias (Union[Unset, str]):
        idp_user_id (Union[Unset, str]):
        last_name (Union[Unset, str]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['UserRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
brief_representation=brief_representation,
email=email,
email_verified=email_verified,
enabled=enabled,
exact=exact,
first=first,
first_name=first_name,
idp_alias=idp_alias,
idp_user_id=idp_user_id,
last_name=last_name,
max_=max_,
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
    brief_representation: Union[Unset, bool] = UNSET,
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    idp_alias: Union[Unset, str] = UNSET,
    idp_user_id: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Union[Any, list['UserRepresentation']] | None:
    """ Get users Returns a stream of users, filtered according to query parameters.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):
        first_name (Union[Unset, str]):
        idp_alias (Union[Unset, str]):
        idp_user_id (Union[Unset, str]):
        last_name (Union[Unset, str]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['UserRepresentation']]
     """


    return sync_detailed(
        realm=realm,
client=client,
brief_representation=brief_representation,
email=email,
email_verified=email_verified,
enabled=enabled,
exact=exact,
first=first,
first_name=first_name,
idp_alias=idp_alias,
idp_user_id=idp_user_id,
last_name=last_name,
max_=max_,
q=q,
search=search,
username=username,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = UNSET,
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    idp_alias: Union[Unset, str] = UNSET,
    idp_user_id: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['UserRepresentation']]]:
    """ Get users Returns a stream of users, filtered according to query parameters.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):
        first_name (Union[Unset, str]):
        idp_alias (Union[Unset, str]):
        idp_user_id (Union[Unset, str]):
        last_name (Union[Unset, str]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['UserRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
brief_representation=brief_representation,
email=email,
email_verified=email_verified,
enabled=enabled,
exact=exact,
first=first,
first_name=first_name,
idp_alias=idp_alias,
idp_user_id=idp_user_id,
last_name=last_name,
max_=max_,
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
    brief_representation: Union[Unset, bool] = UNSET,
    email: Union[Unset, str] = UNSET,
    email_verified: Union[Unset, bool] = UNSET,
    enabled: Union[Unset, bool] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    first: Union[Unset, int] = UNSET,
    first_name: Union[Unset, str] = UNSET,
    idp_alias: Union[Unset, str] = UNSET,
    idp_user_id: Union[Unset, str] = UNSET,
    last_name: Union[Unset, str] = UNSET,
    max_: Union[Unset, int] = UNSET,
    q: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,

) -> Union[Any, list['UserRepresentation']] | None:
    """ Get users Returns a stream of users, filtered according to query parameters.

    Args:
        realm (str):
        brief_representation (Union[Unset, bool]):
        email (Union[Unset, str]):
        email_verified (Union[Unset, bool]):
        enabled (Union[Unset, bool]):
        exact (Union[Unset, bool]):
        first (Union[Unset, int]):
        first_name (Union[Unset, str]):
        idp_alias (Union[Unset, str]):
        idp_user_id (Union[Unset, str]):
        last_name (Union[Unset, str]):
        max_ (Union[Unset, int]):
        q (Union[Unset, str]):
        search (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['UserRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
brief_representation=brief_representation,
email=email,
email_verified=email_verified,
enabled=enabled,
exact=exact,
first=first,
first_name=first_name,
idp_alias=idp_alias,
idp_user_id=idp_user_id,
last_name=last_name,
max_=max_,
q=q,
search=search,
username=username,

    )).parsed
