from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.post_admin_realms_realm_partial_import_response_200 import PostAdminRealmsRealmPartialImportResponse200
from ...types import File, FileTypes
from io import BytesIO
from typing import cast



def _get_kwargs(
    realm: str,
    *,
    body: File,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/admin/realms/{realm}/partialImport".format(realm=realm,),
    }

    _kwargs["json"] = body.to_tuple()




    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, PostAdminRealmsRealmPartialImportResponse200] | None:
    if response.status_code == 200:
        response_200 = PostAdminRealmsRealmPartialImportResponse200.from_dict(response.json())



        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, PostAdminRealmsRealmPartialImportResponse200]]:
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
    body: File,

) -> Response[Union[Any, PostAdminRealmsRealmPartialImportResponse200]]:
    """ Partial import from a JSON file to an existing realm.

    Args:
        realm (str):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostAdminRealmsRealmPartialImportResponse200]]
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
    body: File,

) -> Union[Any, PostAdminRealmsRealmPartialImportResponse200] | None:
    """ Partial import from a JSON file to an existing realm.

    Args:
        realm (str):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostAdminRealmsRealmPartialImportResponse200]
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
    body: File,

) -> Response[Union[Any, PostAdminRealmsRealmPartialImportResponse200]]:
    """ Partial import from a JSON file to an existing realm.

    Args:
        realm (str):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostAdminRealmsRealmPartialImportResponse200]]
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
    body: File,

) -> Union[Any, PostAdminRealmsRealmPartialImportResponse200] | None:
    """ Partial import from a JSON file to an existing realm.

    Args:
        realm (str):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostAdminRealmsRealmPartialImportResponse200]
     """


    return (await asyncio_detailed(
        realm=realm,
client=client,
body=body,

    )).parsed
