from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_graph_request import CreateGraphRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.task_response import TaskResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
  *,
  body: CreateGraphRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
  headers: dict[str, Any] = {}
  if not isinstance(authorization, Unset):
    headers["authorization"] = authorization

  cookies = {}
  if auth_token is not UNSET:
    cookies["auth-token"] = auth_token

  _kwargs: dict[str, Any] = {
    "method": "post",
    "url": "/v1/create/graph",
    "cookies": cookies,
  }

  _kwargs["json"] = body.to_dict()

  headers["Content-Type"] = "application/json"

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, TaskResponse]]:
  if response.status_code == 202:
    response_202 = TaskResponse.from_dict(response.json())

    return response_202
  if response.status_code == 422:
    response_422 = HTTPValidationError.from_dict(response.json())

    return response_422
  if client.raise_on_unexpected_status:
    raise errors.UnexpectedStatus(response.status_code, response.content)
  else:
    return None


def _build_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, TaskResponse]]:
  return Response(
    status_code=HTTPStatus(response.status_code),
    content=response.content,
    headers=response.headers,
    parsed=_parse_response(client=client, response=response),
  )


def sync_detailed(
  *,
  client: AuthenticatedClient,
  body: CreateGraphRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, TaskResponse]]:
  """Create New Graph Database

   Create a new graph database with specified schema and configuration

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CreateGraphRequest): Request model for creating a new graph.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[HTTPValidationError, TaskResponse]]
  """

  kwargs = _get_kwargs(
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = client.get_httpx_client().request(
    **kwargs,
  )

  return _build_response(client=client, response=response)


def sync(
  *,
  client: AuthenticatedClient,
  body: CreateGraphRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, TaskResponse]]:
  """Create New Graph Database

   Create a new graph database with specified schema and configuration

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CreateGraphRequest): Request model for creating a new graph.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[HTTPValidationError, TaskResponse]
  """

  return sync_detailed(
    client=client,
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  *,
  client: AuthenticatedClient,
  body: CreateGraphRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, TaskResponse]]:
  """Create New Graph Database

   Create a new graph database with specified schema and configuration

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CreateGraphRequest): Request model for creating a new graph.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[HTTPValidationError, TaskResponse]]
  """

  kwargs = _get_kwargs(
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  *,
  client: AuthenticatedClient,
  body: CreateGraphRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, TaskResponse]]:
  """Create New Graph Database

   Create a new graph database with specified schema and configuration

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CreateGraphRequest): Request model for creating a new graph.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[HTTPValidationError, TaskResponse]
  """

  return (
    await asyncio_detailed(
      client=client,
      body=body,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
