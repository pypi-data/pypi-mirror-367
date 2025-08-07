from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.member_representation import MemberRepresentation
from typing import cast



def _get_kwargs(
    realm: str,
    org_id: str,
    member_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/organizations/{org_id}/members/{member_id}".format(realm=realm,org_id=org_id,member_id=member_id,),
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, MemberRepresentation] | None:
    if response.status_code == 200:
        response_200 = MemberRepresentation.from_dict(response.json())



        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, MemberRepresentation]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    org_id: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, MemberRepresentation]]:
    """ Returns the member of the organization with the specified id

     Searches for auser with the given id. If one is found, and is currently a member of the
    organization, returns it. Otherwise,an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, MemberRepresentation]]
     """


    kwargs = _get_kwargs(
        realm=realm,
org_id=org_id,
member_id=member_id,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    org_id: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, MemberRepresentation] | None:
    """ Returns the member of the organization with the specified id

     Searches for auser with the given id. If one is found, and is currently a member of the
    organization, returns it. Otherwise,an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, MemberRepresentation]
     """


    return sync_detailed(
        realm=realm,
org_id=org_id,
member_id=member_id,
client=client,

    ).parsed

async def asyncio_detailed(
    realm: str,
    org_id: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Response[Union[Any, MemberRepresentation]]:
    """ Returns the member of the organization with the specified id

     Searches for auser with the given id. If one is found, and is currently a member of the
    organization, returns it. Otherwise,an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, MemberRepresentation]]
     """


    kwargs = _get_kwargs(
        realm=realm,
org_id=org_id,
member_id=member_id,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    org_id: str,
    member_id: str,
    *,
    client: Union[AuthenticatedClient, Client],

) -> Union[Any, MemberRepresentation] | None:
    """ Returns the member of the organization with the specified id

     Searches for auser with the given id. If one is found, and is currently a member of the
    organization, returns it. Otherwise,an error response with status NOT_FOUND is returned

    Args:
        realm (str):
        org_id (str):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, MemberRepresentation]
     """


    return (await asyncio_detailed(
        realm=realm,
org_id=org_id,
member_id=member_id,
client=client,

    )).parsed
