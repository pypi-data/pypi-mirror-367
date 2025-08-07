from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_authentication_unregistered_required_actions_response_200_item import GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item
from typing import cast



def _get_kwargs(
    realm: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/authentication/unregistered-required-actions".format(realm=realm,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']]:
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

) -> Response[list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']]:
    """ Get unregistered required actions Returns a stream of unregistered required actions.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']]
     """


    kwargs = _get_kwargs(
        realm=realm,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item'] | None:
    """ Get unregistered required actions Returns a stream of unregistered required actions.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']
     """


    return sync_detailed(
        realm=realm,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']]:
    """ Get unregistered required actions Returns a stream of unregistered required actions.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']]
     """


    kwargs = _get_kwargs(
        realm=realm,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item'] | None:
    """ Get unregistered required actions Returns a stream of unregistered required actions.

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GetAdminRealmsRealmAuthenticationUnregisteredRequiredActionsResponse200Item']
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,

    )).parsed
