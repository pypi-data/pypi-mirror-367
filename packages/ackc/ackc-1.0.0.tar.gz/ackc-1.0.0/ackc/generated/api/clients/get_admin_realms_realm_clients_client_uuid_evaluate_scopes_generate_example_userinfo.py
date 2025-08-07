from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_clients_client_uuid_evaluate_scopes_generate_example_userinfo_response_200 import GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    scope: Union[Unset, str] = UNSET,
    user_id: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["scope"] = scope

    params["userId"] = user_id


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/evaluate-scopes/generate-example-userinfo".format(realm=realm,client_uuid=client_uuid,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200] | None:
    if response.status_code == 200:
        response_200 = GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200.from_dict(response.json())



        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    scope: Union[Unset, str] = UNSET,
    user_id: Union[Unset, str] = UNSET,

) -> Response[Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]]:
    """ Create JSON with payload of example user info

    Args:
        realm (str):
        client_uuid (str):
        scope (Union[Unset, str]):
        user_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
scope=scope,
user_id=user_id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    scope: Union[Unset, str] = UNSET,
    user_id: Union[Unset, str] = UNSET,

) -> Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200] | None:
    """ Create JSON with payload of example user info

    Args:
        realm (str):
        client_uuid (str):
        scope (Union[Unset, str]):
        user_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
scope=scope,
user_id=user_id,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    scope: Union[Unset, str] = UNSET,
    user_id: Union[Unset, str] = UNSET,

) -> Response[Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]]:
    """ Create JSON with payload of example user info

    Args:
        realm (str):
        client_uuid (str):
        scope (Union[Unset, str]):
        user_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
scope=scope,
user_id=user_id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    scope: Union[Unset, str] = UNSET,
    user_id: Union[Unset, str] = UNSET,

) -> Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200] | None:
    """ Create JSON with payload of example user info

    Args:
        realm (str):
        client_uuid (str):
        scope (Union[Unset, str]):
        user_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetAdminRealmsRealmClientsClientUuidEvaluateScopesGenerateExampleUserinfoResponse200]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
scope=scope,
user_id=user_id,

    )).parsed
