from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.realm_events_config_representation import RealmEventsConfigRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    *,
    body: RealmEventsConfigRepresentation,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/realms/{realm}/events/config".format(realm=realm,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Any | None:
    if response.status_code == 204:
        return None
    if response.status_code == 403:
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
    *,
    client: Union[AuthenticatedClient, Client],
    body: RealmEventsConfigRepresentation,

) -> Response[Any]:
    """  Update the events provider Change the events provider and/or its configuration

    Args:
        realm (str):
        body (RealmEventsConfigRepresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RealmEventsConfigRepresentation,

) -> Response[Any]:
    """  Update the events provider Change the events provider and/or its configuration

    Args:
        realm (str):
        body (RealmEventsConfigRepresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

