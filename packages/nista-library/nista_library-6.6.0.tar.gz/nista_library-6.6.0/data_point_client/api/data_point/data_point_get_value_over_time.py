from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

import datetime
from typing import Dict
from dateutil.parser import isoparse
from typing import Union
from typing import cast
from typing import Optional
from ...models.value_over_time_response import ValueOverTimeResponse
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Unset



def _get_kwargs(
    workspace_id: str,
    data_point_id: str,
    *,
    client: Client,
    start: Union[Unset, None, datetime.datetime] = UNSET,
    end: Union[Unset, None, datetime.datetime] = UNSET,

) -> Dict[str, Any]:
    url = "{}/DataPoint/workspace/{workspaceId}/dataPoint/{dataPointId}/ValueOverTime".format(
        client.base_url,workspaceId=workspace_id,dataPointId=data_point_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    

    

    params: Dict[str, Any] = {}
    json_start: Union[Unset, None, str] = UNSET
    if not isinstance(start, Unset):
        json_start = start.isoformat() if start else None

    params["start"] = json_start


    json_end: Union[Unset, None, str] = UNSET
    if not isinstance(end, Unset):
        json_end = end.isoformat() if end else None

    params["end"] = json_end



    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    

    

    return {
	    "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "params": params,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ProblemDetails, ValueOverTimeResponse]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ValueOverTimeResponse.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ProblemDetails.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ProblemDetails.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ProblemDetails.from_dict(response.json())



        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ProblemDetails.from_dict(response.json())



        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ProblemDetails, ValueOverTimeResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    data_point_id: str,
    *,
    client: Client,
    start: Union[Unset, None, datetime.datetime] = UNSET,
    end: Union[Unset, None, datetime.datetime] = UNSET,

) -> Response[Union[ProblemDetails, ValueOverTimeResponse]]:
    """ 
    Args:
        workspace_id (str):
        data_point_id (str):
        start (Union[Unset, None, datetime.datetime]):
        end (Union[Unset, None, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProblemDetails, ValueOverTimeResponse]]
     """


    kwargs = _get_kwargs(
        workspace_id=workspace_id,
data_point_id=data_point_id,
client=client,
start=start,
end=end,

    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    workspace_id: str,
    data_point_id: str,
    *,
    client: Client,
    start: Union[Unset, None, datetime.datetime] = UNSET,
    end: Union[Unset, None, datetime.datetime] = UNSET,

) -> Optional[Union[ProblemDetails, ValueOverTimeResponse]]:
    """ 
    Args:
        workspace_id (str):
        data_point_id (str):
        start (Union[Unset, None, datetime.datetime]):
        end (Union[Unset, None, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProblemDetails, ValueOverTimeResponse]
     """


    return sync_detailed(
        workspace_id=workspace_id,
data_point_id=data_point_id,
client=client,
start=start,
end=end,

    ).parsed

async def asyncio_detailed(
    workspace_id: str,
    data_point_id: str,
    *,
    client: Client,
    start: Union[Unset, None, datetime.datetime] = UNSET,
    end: Union[Unset, None, datetime.datetime] = UNSET,

) -> Response[Union[ProblemDetails, ValueOverTimeResponse]]:
    """ 
    Args:
        workspace_id (str):
        data_point_id (str):
        start (Union[Unset, None, datetime.datetime]):
        end (Union[Unset, None, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProblemDetails, ValueOverTimeResponse]]
     """


    kwargs = _get_kwargs(
        workspace_id=workspace_id,
data_point_id=data_point_id,
client=client,
start=start,
end=end,

    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(
            **kwargs
        )

    return _build_response(client=client, response=response)

async def asyncio(
    workspace_id: str,
    data_point_id: str,
    *,
    client: Client,
    start: Union[Unset, None, datetime.datetime] = UNSET,
    end: Union[Unset, None, datetime.datetime] = UNSET,

) -> Optional[Union[ProblemDetails, ValueOverTimeResponse]]:
    """ 
    Args:
        workspace_id (str):
        data_point_id (str):
        start (Union[Unset, None, datetime.datetime]):
        end (Union[Unset, None, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProblemDetails, ValueOverTimeResponse]
     """


    return (await asyncio_detailed(
        workspace_id=workspace_id,
data_point_id=data_point_id,
client=client,
start=start,
end=end,

    )).parsed
