from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cypher_query_response import CypherQueryResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
  query_id: str,
  *,
  wait: Union[Unset, int] = 0,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
  headers: dict[str, Any] = {}
  if not isinstance(authorization, Unset):
    headers["authorization"] = authorization

  cookies = {}
  if auth_token is not UNSET:
    cookies["auth-token"] = auth_token

  params: dict[str, Any] = {}

  params["wait"] = wait

  params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

  _kwargs: dict[str, Any] = {
    "method": "get",
    "url": f"/v1/{graph_id}/graph/query/{query_id}/result",
    "params": params,
    "cookies": cookies,
  }

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  if response.status_code == 200:
    response_200 = CypherQueryResponse.from_dict(response.json())

    return response_200
  if response.status_code == 202:
    response_202 = cast(Any, None)
    return response_202
  if response.status_code == 403:
    response_403 = cast(Any, None)
    return response_403
  if response.status_code == 404:
    response_404 = cast(Any, None)
    return response_404
  if response.status_code == 500:
    response_500 = cast(Any, None)
    return response_500
  if response.status_code == 422:
    response_422 = HTTPValidationError.from_dict(response.json())

    return response_422
  if client.raise_on_unexpected_status:
    raise errors.UnexpectedStatus(response.status_code, response.content)
  else:
    return None


def _build_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  return Response(
    status_code=HTTPStatus(response.status_code),
    content=response.content,
    headers=response.headers,
    parsed=_parse_response(client=client, response=response),
  )


def sync_detailed(
  graph_id: str,
  query_id: str,
  *,
  client: AuthenticatedClient,
  wait: Union[Unset, int] = 0,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Get Query Result

   Get the result of a queued query with optional long polling.

  Supports long polling to wait for query completion, reducing the need for frequent
  status checks. The endpoint will wait up to the specified time for the query to
  complete before returning.

  Credit consumption:
  - Credits are consumed when the query completes successfully
  - Failed queries do not consume credits
  - Status checks and polling do not consume credits

  Long polling:
  - `wait=0`: Return immediately (default)
  - `wait=1-30`: Wait up to N seconds for completion
  - Automatically handles timeouts and cancellations

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      wait (Union[Unset, int]):  Default: 0.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, CypherQueryResponse, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    query_id=query_id,
    wait=wait,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = client.get_httpx_client().request(
    **kwargs,
  )

  return _build_response(client=client, response=response)


def sync(
  graph_id: str,
  query_id: str,
  *,
  client: AuthenticatedClient,
  wait: Union[Unset, int] = 0,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Get Query Result

   Get the result of a queued query with optional long polling.

  Supports long polling to wait for query completion, reducing the need for frequent
  status checks. The endpoint will wait up to the specified time for the query to
  complete before returning.

  Credit consumption:
  - Credits are consumed when the query completes successfully
  - Failed queries do not consume credits
  - Status checks and polling do not consume credits

  Long polling:
  - `wait=0`: Return immediately (default)
  - `wait=1-30`: Wait up to N seconds for completion
  - Automatically handles timeouts and cancellations

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      wait (Union[Unset, int]):  Default: 0.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, CypherQueryResponse, HTTPValidationError]
  """

  return sync_detailed(
    graph_id=graph_id,
    query_id=query_id,
    client=client,
    wait=wait,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  graph_id: str,
  query_id: str,
  *,
  client: AuthenticatedClient,
  wait: Union[Unset, int] = 0,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Get Query Result

   Get the result of a queued query with optional long polling.

  Supports long polling to wait for query completion, reducing the need for frequent
  status checks. The endpoint will wait up to the specified time for the query to
  complete before returning.

  Credit consumption:
  - Credits are consumed when the query completes successfully
  - Failed queries do not consume credits
  - Status checks and polling do not consume credits

  Long polling:
  - `wait=0`: Return immediately (default)
  - `wait=1-30`: Wait up to N seconds for completion
  - Automatically handles timeouts and cancellations

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      wait (Union[Unset, int]):  Default: 0.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, CypherQueryResponse, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    query_id=query_id,
    wait=wait,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  graph_id: str,
  query_id: str,
  *,
  client: AuthenticatedClient,
  wait: Union[Unset, int] = 0,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Get Query Result

   Get the result of a queued query with optional long polling.

  Supports long polling to wait for query completion, reducing the need for frequent
  status checks. The endpoint will wait up to the specified time for the query to
  complete before returning.

  Credit consumption:
  - Credits are consumed when the query completes successfully
  - Failed queries do not consume credits
  - Status checks and polling do not consume credits

  Long polling:
  - `wait=0`: Return immediately (default)
  - `wait=1-30`: Wait up to N seconds for completion
  - Automatically handles timeouts and cancellations

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      wait (Union[Unset, int]):  Default: 0.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, CypherQueryResponse, HTTPValidationError]
  """

  return (
    await asyncio_detailed(
      graph_id=graph_id,
      query_id=query_id,
      client=client,
      wait=wait,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
