from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_representation import ErrorRepresentation
from ...models.post_admin_realms_realm_users_user_id_impersonation_response_200 import PostAdminRealmsRealmUsersUserIdImpersonationResponse200
from typing import cast



def _get_kwargs(
    realm: str,
    user_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/users/{user_id}/impersonation".format(realm=realm,user_id=user_id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200] | None:
    if response.status_code == 200:
        response_200 = PostAdminRealmsRealmUsersUserIdImpersonationResponse200.from_dict(response.json())



        return response_200
    if response.status_code == 400:
        response_400 = ErrorRepresentation.from_dict(response.json())



        return response_400
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]]:
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

) -> Response[Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]]:
    """ Impersonate the user

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]]
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

) -> Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200] | None:
    """ Impersonate the user

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]
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

) -> Response[Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]]:
    """ Impersonate the user

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]]
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

) -> Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200] | None:
    """ Impersonate the user

    Args:
        realm (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorRepresentation, PostAdminRealmsRealmUsersUserIdImpersonationResponse200]
     """


    return (await asyncio_detailed(
        realm=realm,
user_id=user_id,
client=client,

    )).parsed
