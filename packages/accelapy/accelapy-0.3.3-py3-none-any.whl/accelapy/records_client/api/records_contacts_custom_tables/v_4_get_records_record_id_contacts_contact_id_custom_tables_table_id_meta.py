from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    record_id: str,
    contact_id: int,
    table_id: str,
    *,
    fields: Union[Unset, None, str] = UNSET,
    lang: Union[Unset, None, str] = UNSET,
    authorization: str,
) -> Dict[str, Any]:
    headers = {}
    headers["Authorization"] = authorization

    params: Dict[str, Any] = {}
    params["fields"] = fields

    params["lang"] = lang

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/v4/records/{recordId}/contacts/{contactId}/customTables/{tableId}/meta".format(
            recordId=record_id,
            contactId=contact_id,
            tableId=table_id,
        ),
        "params": params,
        "headers": headers,
    }


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return None
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        return None
    if response.status_code == HTTPStatus.FORBIDDEN:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    record_id: str,
    contact_id: int,
    table_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Union[Unset, None, str] = UNSET,
    lang: Union[Unset, None, str] = UNSET,
    authorization: str,
) -> Response[Any]:
    """Get Metadata of a Record Contact Custom Table

     Gets the metadata of a specified custom table associated with the specified record contact.



    **API Endpoint**:  GET /v4/records/{recordId}/contacts/{contactId}/customTables/{tableId}/meta

    **Scope**:  records

    **App Type**:  Agency

    **Authorization Type**:  Access token

    **Civic Platform version**: 8.0.3


    Args:
        record_id (str):
        contact_id (int):
        table_id (str):
        fields (Union[Unset, None, str]):
        lang (Union[Unset, None, str]):
        authorization (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        record_id=record_id,
        contact_id=contact_id,
        table_id=table_id,
        fields=fields,
        lang=lang,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    record_id: str,
    contact_id: int,
    table_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Union[Unset, None, str] = UNSET,
    lang: Union[Unset, None, str] = UNSET,
    authorization: str,
) -> Response[Any]:
    """Get Metadata of a Record Contact Custom Table

     Gets the metadata of a specified custom table associated with the specified record contact.



    **API Endpoint**:  GET /v4/records/{recordId}/contacts/{contactId}/customTables/{tableId}/meta

    **Scope**:  records

    **App Type**:  Agency

    **Authorization Type**:  Access token

    **Civic Platform version**: 8.0.3


    Args:
        record_id (str):
        contact_id (int):
        table_id (str):
        fields (Union[Unset, None, str]):
        lang (Union[Unset, None, str]):
        authorization (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        record_id=record_id,
        contact_id=contact_id,
        table_id=table_id,
        fields=fields,
        lang=lang,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
