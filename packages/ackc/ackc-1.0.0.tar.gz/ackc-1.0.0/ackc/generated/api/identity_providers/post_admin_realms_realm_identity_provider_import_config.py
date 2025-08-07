from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.post_admin_realms_realm_identity_provider_import_config_body import PostAdminRealmsRealmIdentityProviderImportConfigBody
from ...models.post_admin_realms_realm_identity_provider_import_config_response_200 import PostAdminRealmsRealmIdentityProviderImportConfigResponse200
from typing import cast



def _get_kwargs(
    realm: str,
    *,
    body: PostAdminRealmsRealmIdentityProviderImportConfigBody,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/identity-provider/import-config".format(realm=realm,),
    }

    _kwargs["json"] = body.to_dict()



    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> PostAdminRealmsRealmIdentityProviderImportConfigResponse200 | None:
    if response.status_code == 200:
        response_200 = PostAdminRealmsRealmIdentityProviderImportConfigResponse200.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[PostAdminRealmsRealmIdentityProviderImportConfigResponse200]:
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
    body: PostAdminRealmsRealmIdentityProviderImportConfigBody,

) -> Response[PostAdminRealmsRealmIdentityProviderImportConfigResponse200]:
    """ Import identity provider from JSON body

     Import identity provider from uploaded JSON file

    Args:
        realm (str):
        body (PostAdminRealmsRealmIdentityProviderImportConfigBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostAdminRealmsRealmIdentityProviderImportConfigResponse200]
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
    body: PostAdminRealmsRealmIdentityProviderImportConfigBody,

) -> PostAdminRealmsRealmIdentityProviderImportConfigResponse200 | None:
    """ Import identity provider from JSON body

     Import identity provider from uploaded JSON file

    Args:
        realm (str):
        body (PostAdminRealmsRealmIdentityProviderImportConfigBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostAdminRealmsRealmIdentityProviderImportConfigResponse200
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
    body: PostAdminRealmsRealmIdentityProviderImportConfigBody,

) -> Response[PostAdminRealmsRealmIdentityProviderImportConfigResponse200]:
    """ Import identity provider from JSON body

     Import identity provider from uploaded JSON file

    Args:
        realm (str):
        body (PostAdminRealmsRealmIdentityProviderImportConfigBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostAdminRealmsRealmIdentityProviderImportConfigResponse200]
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
    body: PostAdminRealmsRealmIdentityProviderImportConfigBody,

) -> PostAdminRealmsRealmIdentityProviderImportConfigResponse200 | None:
    """ Import identity provider from JSON body

     Import identity provider from uploaded JSON file

    Args:
        realm (str):
        body (PostAdminRealmsRealmIdentityProviderImportConfigBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostAdminRealmsRealmIdentityProviderImportConfigResponse200
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
body=body,

    )).parsed
