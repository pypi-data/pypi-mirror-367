from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cancel_query_response_cancelquery import CancelQueryResponseCancelquery
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
  query_id: str,
  *,
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
    "method": "delete",
    "url": f"/v1/{graph_id}/graph/query/{query_id}",
    "cookies": cookies,
  }

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]:
  if response.status_code == 200:
    response_200 = CancelQueryResponseCancelquery.from_dict(response.json())

    return response_200
  if response.status_code == 400:
    response_400 = cast(Any, None)
    return response_400
  if response.status_code == 403:
    response_403 = cast(Any, None)
    return response_403
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
) -> Response[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]:
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
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]:
  """Cancel Query

   Cancel a pending query.

  Only queries that are still pending in the queue can be cancelled.
  Running queries cannot be cancelled and will return an error.

  Returns status information about the cancellation operation.

  No credits are consumed for query cancellation.

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    query_id=query_id,
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
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]:
  """Cancel Query

   Cancel a pending query.

  Only queries that are still pending in the queue can be cancelled.
  Running queries cannot be cancelled and will return an error.

  Returns status information about the cancellation operation.

  No credits are consumed for query cancellation.

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]
  """

  return sync_detailed(
    graph_id=graph_id,
    query_id=query_id,
    client=client,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  graph_id: str,
  query_id: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]:
  """Cancel Query

   Cancel a pending query.

  Only queries that are still pending in the queue can be cancelled.
  Running queries cannot be cancelled and will return an error.

  Returns status information about the cancellation operation.

  No credits are consumed for query cancellation.

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    query_id=query_id,
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
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]]:
  """Cancel Query

   Cancel a pending query.

  Only queries that are still pending in the queue can be cancelled.
  Running queries cannot be cancelled and will return an error.

  Returns status information about the cancellation operation.

  No credits are consumed for query cancellation.

  Args:
      graph_id (str): Graph database identifier
      query_id (str): The query ID
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, CancelQueryResponseCancelquery, HTTPValidationError]
  """

  return (
    await asyncio_detailed(
      graph_id=graph_id,
      query_id=query_id,
      client=client,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
