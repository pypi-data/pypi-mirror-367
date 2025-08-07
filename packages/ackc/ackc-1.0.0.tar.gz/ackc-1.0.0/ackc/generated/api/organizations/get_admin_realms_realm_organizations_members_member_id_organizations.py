from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.organization_representation import OrganizationRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    member_id: str,
    *,
    brief_representation: Union[Unset, bool] = True,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["briefRepresentation"] = brief_representation


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/organizations/members/{member_id}/organizations".format(realm=realm,member_id=member_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['OrganizationRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = OrganizationRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['OrganizationRepresentation']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,

) -> Response[Union[Any, list['OrganizationRepresentation']]]:
    """ Returns the organizations associated with the user that has the specified id

    Args:
        realm (str):
        member_id (str):
        brief_representation (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['OrganizationRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
member_id=member_id,
brief_representation=brief_representation,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,

) -> Union[Any, list['OrganizationRepresentation']] | None:
    """ Returns the organizations associated with the user that has the specified id

    Args:
        realm (str):
        member_id (str):
        brief_representation (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['OrganizationRepresentation']]
     """


    return sync_detailed(
        realm=realm,
member_id=member_id,
client=client,
brief_representation=brief_representation,

    ).parsed

async def asyncio_detailed(
    realm: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,

) -> Response[Union[Any, list['OrganizationRepresentation']]]:
    """ Returns the organizations associated with the user that has the specified id

    Args:
        realm (str):
        member_id (str):
        brief_representation (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['OrganizationRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
member_id=member_id,
brief_representation=brief_representation,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    brief_representation: Union[Unset, bool] = True,

) -> Union[Any, list['OrganizationRepresentation']] | None:
    """ Returns the organizations associated with the user that has the specified id

    Args:
        realm (str):
        member_id (str):
        brief_representation (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['OrganizationRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
member_id=member_id,
client=client,
brief_representation=brief_representation,

    )).parsed
