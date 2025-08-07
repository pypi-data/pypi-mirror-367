from http import HTTPStatus
from typing import Any, Union, cast

import niquests

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_admin_realms_realm_localization_locale_response_200 import GetAdminRealmsRealmLocalizationLocaleResponse200
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    realm: str,
    locale: str,
    *,
    use_realm_default_locale_fallback: Union[Unset, bool] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["useRealmDefaultLocaleFallback"] = use_realm_default_locale_fallback


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/admin/realms/{realm}/localization/{locale}".format(realm=realm,locale=locale,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200] | None:
    if response.status_code == 200:
        response_200 = GetAdminRealmsRealmLocalizationLocaleResponse200.from_dict(response.json())



        return response_200
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: niquests.Response) -> Response[Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    locale: str,
    *,
    client: Union[AuthenticatedClient, Client],
    use_realm_default_locale_fallback: Union[Unset, bool] = UNSET,

) -> Response[Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]]:
    """ 
    Args:
        realm (str):
        locale (str):
        use_realm_default_locale_fallback (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]]
     """


    kwargs = _get_kwargs(
        realm=realm,
locale=locale,
use_realm_default_locale_fallback=use_realm_default_locale_fallback,

    )

    response = client.get_niquests_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    realm: str,
    locale: str,
    *,
    client: Union[AuthenticatedClient, Client],
    use_realm_default_locale_fallback: Union[Unset, bool] = UNSET,

) -> Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200] | None:
    """ 
    Args:
        realm (str):
        locale (str):
        use_realm_default_locale_fallback (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]
     """


    return sync_detailed(
        realm=realm,
locale=locale,
client=client,
use_realm_default_locale_fallback=use_realm_default_locale_fallback,

    ).parsed

async def asyncio_detailed(
    realm: str,
    locale: str,
    *,
    client: Union[AuthenticatedClient, Client],
    use_realm_default_locale_fallback: Union[Unset, bool] = UNSET,

) -> Response[Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]]:
    """ 
    Args:
        realm (str):
        locale (str):
        use_realm_default_locale_fallback (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]]
     """


    kwargs = _get_kwargs(
        realm=realm,
locale=locale,
use_realm_default_locale_fallback=use_realm_default_locale_fallback,

    )

    response = await client.get_async_niquests_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    realm: str,
    locale: str,
    *,
    client: Union[AuthenticatedClient, Client],
    use_realm_default_locale_fallback: Union[Unset, bool] = UNSET,

) -> Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200] | None:
    """ 
    Args:
        realm (str):
        locale (str):
        use_realm_default_locale_fallback (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetAdminRealmsRealmLocalizationLocaleResponse200]
     """


    return (await asyncio_detailed(
        realm=realm,
locale=locale,
client=client,
use_realm_default_locale_fallback=use_realm_default_locale_fallback,

    )).parsed
