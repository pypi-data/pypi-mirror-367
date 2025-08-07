from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.policy_evaluation_request import PolicyEvaluationRequest
from ...models.policy_evaluation_response import PolicyEvaluationResponse
from typing import cast



def _get_kwargs(
    realm: str,
    client_uuid: str,
    *,
    body: PolicyEvaluationRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/clients/{client_uuid}/authz/resource-server/policy/evaluate".format(realm=realm,client_uuid=client_uuid,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, PolicyEvaluationResponse] | None:
    if response.status_code == 200:
        response_200 = PolicyEvaluationResponse.from_dict(response.json())



        return response_200
    if response.status_code == 500:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, PolicyEvaluationResponse]]:
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
    body: PolicyEvaluationRequest,

) -> Response[Union[Any, PolicyEvaluationResponse]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        body (PolicyEvaluationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PolicyEvaluationResponse]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
body=body,

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
    body: PolicyEvaluationRequest,

) -> Union[Any, PolicyEvaluationResponse] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        body (PolicyEvaluationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PolicyEvaluationResponse]
     """


    return sync_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    realm: str,
    client_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PolicyEvaluationRequest,

) -> Response[Union[Any, PolicyEvaluationResponse]]:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        body (PolicyEvaluationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PolicyEvaluationResponse]]
     """


    kwargs = _get_kwargs(
        realm=realm,
client_uuid=client_uuid,
body=body,

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
    body: PolicyEvaluationRequest,

) -> Union[Any, PolicyEvaluationResponse] | None:
    """ 
    Args:
        realm (str):
        client_uuid (str):
        body (PolicyEvaluationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PolicyEvaluationResponse]
     """


    return (await asyncio_detailed(
        realm=realm,
client_uuid=client_uuid,
client=client,
body=body,

    )).parsed
