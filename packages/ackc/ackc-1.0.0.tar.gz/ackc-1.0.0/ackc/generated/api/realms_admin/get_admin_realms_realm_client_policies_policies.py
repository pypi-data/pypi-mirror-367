from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.client_policies_representation import ClientPoliciesRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    *,
    include_global_policies: Union[Unset, bool] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["include-global-policies"] = include_global_policies


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/client-policies/policies".format(realm=realm,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> ClientPoliciesRepresentation | None:
    if response.status_code == 200:
        response_200 = ClientPoliciesRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[ClientPoliciesRepresentation]:
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
    include_global_policies: Union[Unset, bool] = UNSET,

) -> Response[ClientPoliciesRepresentation]:
    """ 
    Args:
        realm (str):
        include_global_policies (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientPoliciesRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
include_global_policies=include_global_policies,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_global_policies: Union[Unset, bool] = UNSET,

) -> ClientPoliciesRepresentation | None:
    """ 
    Args:
        realm (str):
        include_global_policies (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientPoliciesRepresentation
     """


    return sync_detailed(
        realm=realm,
client=client,
include_global_policies=include_global_policies,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_global_policies: Union[Unset, bool] = UNSET,

) -> Response[ClientPoliciesRepresentation]:
    """ 
    Args:
        realm (str):
        include_global_policies (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientPoliciesRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
include_global_policies=include_global_policies,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_global_policies: Union[Unset, bool] = UNSET,

) -> ClientPoliciesRepresentation | None:
    """ 
    Args:
        realm (str):
        include_global_policies (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientPoliciesRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
include_global_policies=include_global_policies,

    )).parsed
