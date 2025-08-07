from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.abstract_policy_representation import AbstractPolicyRepresentation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    fields: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    permission: Union[Unset, bool] = UNSET,
    policy_id: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    resource_type: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["fields"] = fields

    params["first"] = first

    params["max"] = max_

    params["name"] = name

    params["owner"] = owner

    params["permission"] = permission

    params["policyId"] = policy_id

    params["resource"] = resource

    params["resourceType"] = resource_type

    params["scope"] = scope

    params["type"] = type_


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/policy".format(realm=realm,client_uuid=client_uuid,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, list['AbstractPolicyRepresentation']] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = AbstractPolicyRepresentation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, list['AbstractPolicyRepresentation']]]:
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
    fields: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    permission: Union[Unset, bool] = UNSET,
    policy_id: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    resource_type: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['AbstractPolicyRepresentation']]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        permission (Union[Unset, bool]):
        policy_id (Union[Unset, str]):
        resource (Union[Unset, str]):
        resource_type (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['AbstractPolicyRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
fields=fields,
first=first,
max_=max_,
name=name,
owner=owner,
permission=permission,
policy_id=policy_id,
resource=resource,
resource_type=resource_type,
scope=scope,
type_=type_,

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
    fields: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    permission: Union[Unset, bool] = UNSET,
    policy_id: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    resource_type: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> Union[Any, list['AbstractPolicyRepresentation']] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        permission (Union[Unset, bool]):
        policy_id (Union[Unset, str]):
        resource (Union[Unset, str]):
        resource_type (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['AbstractPolicyRepresentation']]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
fields=fields,
first=first,
max_=max_,
name=name,
owner=owner,
permission=permission,
policy_id=policy_id,
resource=resource,
resource_type=resource_type,
scope=scope,
type_=type_,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    permission: Union[Unset, bool] = UNSET,
    policy_id: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    resource_type: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> Response[Union[Any, list['AbstractPolicyRepresentation']]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        permission (Union[Unset, bool]):
        policy_id (Union[Unset, str]):
        resource (Union[Unset, str]):
        resource_type (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['AbstractPolicyRepresentation']]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
fields=fields,
first=first,
max_=max_,
name=name,
owner=owner,
permission=permission,
policy_id=policy_id,
resource=resource,
resource_type=resource_type,
scope=scope,
type_=type_,

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
    fields: Union[Unset, str] = UNSET,
    first: Union[Unset, int] = UNSET,
    max_: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    owner: Union[Unset, str] = UNSET,
    permission: Union[Unset, bool] = UNSET,
    policy_id: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    resource_type: Union[Unset, str] = UNSET,
    scope: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,

) -> Union[Any, list['AbstractPolicyRepresentation']] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        fields (Union[Unset, str]):
        first (Union[Unset, int]):
        max_ (Union[Unset, int]):
        name (Union[Unset, str]):
        owner (Union[Unset, str]):
        permission (Union[Unset, bool]):
        policy_id (Union[Unset, str]):
        resource (Union[Unset, str]):
        resource_type (Union[Unset, str]):
        scope (Union[Unset, str]):
        type_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['AbstractPolicyRepresentation']]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
fields=fields,
first=first,
max_=max_,
name=name,
owner=owner,
permission=permission,
policy_id=policy_id,
resource=resource,
resource_type=resource_type,
scope=scope,
type_=type_,

    )).parsed
