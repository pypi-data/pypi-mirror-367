from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.user_session_representation import UserSessionRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    user_id: str,
    client_uuid: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/users/{user_id}/offline-sessions/{client_uuid}".format(realm=realm,user_id=user_id,client_uuid=client_uuid,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['UserSessionRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = UserSessionRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['UserSessionRepresentation']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    user_id: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, list['UserSessionRepresentation']]]:
    """ Get offline sessions associated with the user and client

    Args:
        realm (str):
        user_id (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['UserSessionRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
user_id=user_id,
client_uuid=client_uuid,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    user_id: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, list['UserSessionRepresentation']] | None:
    """ Get offline sessions associated with the user and client

    Args:
        realm (str):
        user_id (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['UserSessionRepresentation']]
     """


    return sync_detailed(
        realm=realm,
user_id=user_id,
client_uuid=client_uuid,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    user_id: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, list['UserSessionRepresentation']]]:
    """ Get offline sessions associated with the user and client

    Args:
        realm (str):
        user_id (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['UserSessionRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
user_id=user_id,
client_uuid=client_uuid,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    user_id: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, list['UserSessionRepresentation']] | None:
    """ Get offline sessions associated with the user and client

    Args:
        realm (str):
        user_id (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['UserSessionRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
user_id=user_id,
client_uuid=client_uuid,
client=client,

    )).parsed
