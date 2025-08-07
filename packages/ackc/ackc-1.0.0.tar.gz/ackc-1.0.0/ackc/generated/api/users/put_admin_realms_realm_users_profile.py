from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.up_config import UPConfig
from typing import cast



def _get_kwargs(
    realm: str,
    *,
    body: UPConfig,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/admin/realms/{realm}/users/profile".format(realm=realm,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, UPConfig] | None:
    if response.status_code == 200:
        response_200 = UPConfig.from_dict(response.json())



        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, UPConfig]]:
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
    body: UPConfig,

) -> Response[Union[Any, UPConfig]]:
    """  Set the configuration for the user profile

    Args:
        realm (str):
        body (UPConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UPConfig]]
     """


    kwargs = _get_kwargs(
        realm=realm,
body=body,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UPConfig,

) -> Union[Any, UPConfig] | None:
    """  Set the configuration for the user profile

    Args:
        realm (str):
        body (UPConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UPConfig]
     """


    return sync_detailed(
        realm=realm,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UPConfig,

) -> Response[Union[Any, UPConfig]]:
    """  Set the configuration for the user profile

    Args:
        realm (str):
        body (UPConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UPConfig]]
     """


    kwargs = _get_kwargs(
        realm=realm,
body=body,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UPConfig,

) -> Union[Any, UPConfig] | None:
    """  Set the configuration for the user profile

    Args:
        realm (str):
        body (UPConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UPConfig]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
body=body,

    )).parsed
