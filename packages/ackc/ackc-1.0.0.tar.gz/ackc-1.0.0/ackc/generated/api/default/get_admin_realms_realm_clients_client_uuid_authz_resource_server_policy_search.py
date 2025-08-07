from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.abstract_policy_representation import AbstractPolicyRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    fields: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["fields"] = fields

    params["name"] = name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/policy/search".format(realm=realm,client_uuid=client_uuid,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[AbstractPolicyRepresentation, Any] | None:
    if response.status_code == 200:
        response_200 = AbstractPolicyRepresentation.from_dict(response.json())



        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[AbstractPolicyRepresentation, Any]]:
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
    fields: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,

) -> Response[Union[AbstractPolicyRepresentation, Any]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AbstractPolicyRepresentation, Any]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
fields=fields,
name=name,

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
    fields: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,

) -> Union[AbstractPolicyRepresentation, Any] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AbstractPolicyRepresentation, Any]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
fields=fields,
name=name,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,

) -> Response[Union[AbstractPolicyRepresentation, Any]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AbstractPolicyRepresentation, Any]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
fields=fields,
name=name,

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
    fields: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,

) -> Union[AbstractPolicyRepresentation, Any] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AbstractPolicyRepresentation, Any]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
fields=fields,
name=name,

    )).parsed
