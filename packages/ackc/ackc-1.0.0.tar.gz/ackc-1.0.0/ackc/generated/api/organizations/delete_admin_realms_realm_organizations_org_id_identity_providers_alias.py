from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    realm: str,
    org_id: str,
    alias: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/admin/realms/{realm}/organizations/{org_id}/identity-providers/{alias}".format(realm=realm,org_id=org_id,alias=alias,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Any | None:
    if response.status_code == 204:
        return None
    if response.status_code == 400:
        return None
    if response.status_code == 404:
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
    org_id: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Any]:
    """ Removes the identity provider with the specified alias from the organization

     Breaks the association between the identity provider and the organization. The provider itself is
    not deleted. If no provider is found, or if it is not currently associated with the org, an error
    response is returned

    Args:
        realm (str):
        org_id (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
org_id=org_id,
alias=alias,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    realm: str,
    org_id: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Any]:
    """ Removes the identity provider with the specified alias from the organization

     Breaks the association between the identity provider and the organization. The provider itself is
    not deleted. If no provider is found, or if it is not currently associated with the org, an error
    response is returned

    Args:
        realm (str):
        org_id (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        realm=realm,
org_id=org_id,
alias=alias,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

