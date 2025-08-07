from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.role_representation import RoleRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    role_name: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/roles/{role_name}/composites/realm".format(realm=realm,role_name=role_name,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['RoleRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = RoleRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['RoleRepresentation']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    role_name: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, list['RoleRepresentation']]]:
    """ Get realm-level roles of the role's composite

    Args:
        realm (str):
        role_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['RoleRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
role_name=role_name,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    role_name: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, list['RoleRepresentation']] | None:
    """ Get realm-level roles of the role's composite

    Args:
        realm (str):
        role_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['RoleRepresentation']]
     """


    return sync_detailed(
        realm=realm,
role_name=role_name,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    role_name: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, list['RoleRepresentation']]]:
    """ Get realm-level roles of the role's composite

    Args:
        realm (str):
        role_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['RoleRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
role_name=role_name,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    role_name: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, list['RoleRepresentation']] | None:
    """ Get realm-level roles of the role's composite

    Args:
        realm (str):
        role_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['RoleRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
role_name=role_name,
client=client,

    )).parsed
