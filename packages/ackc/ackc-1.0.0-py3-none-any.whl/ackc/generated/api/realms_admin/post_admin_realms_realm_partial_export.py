from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.realm_representation import RealmRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    export_clients: Union[Unset, bool] = UNSET,
    export_groups_and_roles: Union[Unset, bool] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["exportClients"] = export_clients

    params["exportGroupsAndRoles"] = export_groups_and_roles


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/partial-export".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, RealmRepresentation] | None:
    if response.status_code == 200:
        response_200 = RealmRepresentation.from_dict(response.json())



        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, RealmRepresentation]]:
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
    export_clients: Union[Unset, bool] = UNSET,
    export_groups_and_roles: Union[Unset, bool] = UNSET,

) -> Response[Union[Any, RealmRepresentation]]:
    """ Partial export of existing realm into a JSON file.

    Args:
        realm (str):
        export_clients (Union[Unset, bool]):
        export_groups_and_roles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, RealmRepresentation]]
     """


    kwargs = _get_kwargs(
        realm=realm,
export_clients=export_clients,
export_groups_and_roles=export_groups_and_roles,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    export_clients: Union[Unset, bool] = UNSET,
    export_groups_and_roles: Union[Unset, bool] = UNSET,

) -> Union[Any, RealmRepresentation] | None:
    """ Partial export of existing realm into a JSON file.

    Args:
        realm (str):
        export_clients (Union[Unset, bool]):
        export_groups_and_roles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, RealmRepresentation]
     """


    return sync_detailed(
        realm=realm,
client=client,
export_clients=export_clients,
export_groups_and_roles=export_groups_and_roles,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    export_clients: Union[Unset, bool] = UNSET,
    export_groups_and_roles: Union[Unset, bool] = UNSET,

) -> Response[Union[Any, RealmRepresentation]]:
    """ Partial export of existing realm into a JSON file.

    Args:
        realm (str):
        export_clients (Union[Unset, bool]):
        export_groups_and_roles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, RealmRepresentation]]
     """


    kwargs = _get_kwargs(
        realm=realm,
export_clients=export_clients,
export_groups_and_roles=export_groups_and_roles,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    export_clients: Union[Unset, bool] = UNSET,
    export_groups_and_roles: Union[Unset, bool] = UNSET,

) -> Union[Any, RealmRepresentation] | None:
    """ Partial export of existing realm into a JSON file.

    Args:
        realm (str):
        export_clients (Union[Unset, bool]):
        export_groups_and_roles (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, RealmRepresentation]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
export_clients=export_clients,
export_groups_and_roles=export_groups_and_roles,

    )).parsed
