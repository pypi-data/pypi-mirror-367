from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.credential_representation import CredentialRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    client_uuid: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/client-secret".format(realm=realm,client_uuid=client_uuid,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> CredentialRepresentation | None:
    if response.status_code == 200:
        response_200 = CredentialRepresentation.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[CredentialRepresentation]:
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

) -> Response[CredentialRepresentation]:
    """ Generate a new secret for the client

    Args:
        realm (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CredentialRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,

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

) -> CredentialRepresentation | None:
    """ Generate a new secret for the client

    Args:
        realm (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CredentialRepresentation
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[CredentialRepresentation]:
    """ Generate a new secret for the client

    Args:
        realm (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CredentialRepresentation]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,

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

) -> CredentialRepresentation | None:
    """ Generate a new secret for the client

    Args:
        realm (str):
        client_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CredentialRepresentation
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,

    )).parsed
