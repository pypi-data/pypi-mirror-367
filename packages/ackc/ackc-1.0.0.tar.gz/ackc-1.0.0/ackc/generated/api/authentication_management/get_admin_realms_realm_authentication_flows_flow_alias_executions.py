from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.authentication_execution_info_representation import AuthenticationExecutionInfoRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    flow_alias: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/authentication/flows/{flow_alias}/executions".format(realm=realm,flow_alias=flow_alias,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> list['AuthenticationExecutionInfoRepresentation'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = AuthenticationExecutionInfoRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[list['AuthenticationExecutionInfoRepresentation']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    flow_alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['AuthenticationExecutionInfoRepresentation']]:
    """ Get authentication executions for a flow

    Args:
        realm (str):
        flow_alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AuthenticationExecutionInfoRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
flow_alias=flow_alias,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    flow_alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['AuthenticationExecutionInfoRepresentation'] | None:
    """ Get authentication executions for a flow

    Args:
        realm (str):
        flow_alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AuthenticationExecutionInfoRepresentation']
     """


    return sync_detailed(
        realm=realm,
flow_alias=flow_alias,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    flow_alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[list['AuthenticationExecutionInfoRepresentation']]:
    """ Get authentication executions for a flow

    Args:
        realm (str):
        flow_alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AuthenticationExecutionInfoRepresentation']]
     """


    kwargs = _get_kwargs(
        realm=realm,
flow_alias=flow_alias,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    flow_alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> list['AuthenticationExecutionInfoRepresentation'] | None:
    """ Get authentication executions for a flow

    Args:
        realm (str):
        flow_alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AuthenticationExecutionInfoRepresentation']
     """


    return (await asyncio_detailed(
        realm=realm,
flow_alias=flow_alias,
client=client,

    )).parsed
