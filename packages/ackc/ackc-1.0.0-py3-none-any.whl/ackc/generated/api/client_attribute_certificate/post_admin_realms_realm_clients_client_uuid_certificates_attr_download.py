from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.key_store_config import KeyStoreConfig
from ...types import File, FileTypes
from io import BytesIO
from typing import cast



def _get_kwargs(
    realm: str,
    client_uuid: str,
    attr: str,
    *,
    body: KeyStoreConfig,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/certificates/{attr}/download".format(realm=realm,client_uuid=client_uuid,attr=attr,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> File | None:
    if response.status_code == 200:
        response_200 = File(
             payload = BytesIO(response.content)
        )



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[File]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    client_uuid: str,
    attr: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: KeyStoreConfig,

) -> Response[File]:
    """ Get a keystore file for the client, containing private key and public certificate

    Args:
        realm (str):
        client_uuid (str):
        attr (str):
        body (KeyStoreConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[File]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
attr=attr,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    client_uuid: str,
    attr: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: KeyStoreConfig,

) -> File | None:
    """ Get a keystore file for the client, containing private key and public certificate

    Args:
        realm (str):
        client_uuid (str):
        attr (str):
        body (KeyStoreConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        File
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
attr=attr,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    attr: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: KeyStoreConfig,

) -> Response[File]:
    """ Get a keystore file for the client, containing private key and public certificate

    Args:
        realm (str):
        client_uuid (str):
        attr (str):
        body (KeyStoreConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[File]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
attr=attr,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    client_uuid: str,
    attr: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: KeyStoreConfig,

) -> File | None:
    """ Get a keystore file for the client, containing private key and public certificate

    Args:
        realm (str):
        client_uuid (str):
        attr (str):
        body (KeyStoreConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        File
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
attr=attr,
client=client,
body=body,

    )).parsed
