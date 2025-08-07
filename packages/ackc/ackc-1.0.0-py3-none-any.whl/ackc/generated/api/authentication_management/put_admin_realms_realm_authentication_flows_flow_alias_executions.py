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
    *,
    body: AuthenticationExecutionInfoRepresentation,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/realms/{realm}/authentication/flows/{flow_alias}/executions".format(realm=realm,flow_alias=flow_alias,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Any | None:
    if response.status_code == 204:
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
    flow_alias: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AuthenticationExecutionInfoRepresentation,

) -> Response[Any]:
    """ Update authentication executions of a Flow

    Args:
        realm (str):
        flow_alias (str):
        body (AuthenticationExecutionInfoRepresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
flow_alias=flow_alias,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    realm: str,
    flow_alias: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AuthenticationExecutionInfoRepresentation,

) -> Response[Any]:
    """ Update authentication executions of a Flow

    Args:
        realm (str):
        flow_alias (str):
        body (AuthenticationExecutionInfoRepresentation):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
flow_alias=flow_alias,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

