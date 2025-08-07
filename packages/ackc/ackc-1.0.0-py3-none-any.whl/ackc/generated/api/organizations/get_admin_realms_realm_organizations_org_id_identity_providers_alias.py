from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.identity_provider_representation import IdentityProviderRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    org_id: str,
    alias: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/organizations/{org_id}/identity-providers/{alias}".format(realm=realm,org_id=org_id,alias=alias,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, IdentityProviderRepresentation] | None:
    if response.status_code == 200:
        response_200 = IdentityProviderRepresentation.from_dict(response.json())



        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, IdentityProviderRepresentation]]:
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

) -> Response[Union[Any, IdentityProviderRepresentation]]:
    """ Returns the identity provider associated with the organization that has the specified alias

     Searches for an identity provider with the given alias. If one is found and is associated with the
    organization, it is returned. Otherwise, an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, IdentityProviderRepresentation]]
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

def sync(
    realm: str,
    org_id: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, IdentityProviderRepresentation] | None:
    """ Returns the identity provider associated with the organization that has the specified alias

     Searches for an identity provider with the given alias. If one is found and is associated with the
    organization, it is returned. Otherwise, an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, IdentityProviderRepresentation]
     """


    return sync_detailed(
        realm=realm,
org_id=org_id,
alias=alias,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    org_id: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, IdentityProviderRepresentation]]:
    """ Returns the identity provider associated with the organization that has the specified alias

     Searches for an identity provider with the given alias. If one is found and is associated with the
    organization, it is returned. Otherwise, an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, IdentityProviderRepresentation]]
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

async def asyncio(
    realm: str,
    org_id: str,
    alias: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, IdentityProviderRepresentation] | None:
    """ Returns the identity provider associated with the organization that has the specified alias

     Searches for an identity provider with the given alias. If one is found and is associated with the
    organization, it is returned. Otherwise, an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, IdentityProviderRepresentation]
     """


    return (await asyncio_detailed(
        realm=realm,
org_id=org_id,
alias=alias,
client=client,

    )).parsed
