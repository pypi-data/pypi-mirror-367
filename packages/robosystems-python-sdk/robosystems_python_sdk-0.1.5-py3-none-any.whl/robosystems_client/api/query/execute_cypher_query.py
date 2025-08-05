from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cypher_query_request import CypherQueryRequest
from ...models.cypher_query_response import CypherQueryResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
  *,
  body: CypherQueryRequest,
  streaming: Union[Unset, bool] = False,
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

  params["streaming"] = streaming

  params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

  _kwargs: dict[str, Any] = {
    "method": "post",
    "url": f"/v1/{graph_id}/graph/query",
    "params": params,
    "cookies": cookies,
  }

  _kwargs["json"] = body.to_dict()

  headers["Content-Type"] = "application/json"

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
  if response.status_code == 400:
    response_400 = cast(Any, None)
    return response_400
  if response.status_code == 402:
    response_402 = cast(Any, None)
    return response_402
  if response.status_code == 403:
    response_403 = cast(Any, None)
    return response_403
  if response.status_code == 408:
    response_408 = cast(Any, None)
    return response_408
  if response.status_code == 429:
    response_429 = cast(Any, None)
    return response_429
  if response.status_code == 500:
    response_500 = cast(Any, None)
    return response_500
  if response.status_code == 503:
    response_503 = cast(Any, None)
    return response_503
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
  *,
  client: AuthenticatedClient,
  body: CypherQueryRequest,
  streaming: Union[Unset, bool] = False,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Execute a Cypher query

   Execute a Cypher query against the specified graph database.

  Queries are automatically queued under heavy load for optimal performance.
  Write operations are allowed for users with appropriate permissions:
  - User graphs: member/admin role required
  - Shared repositories: read-only access only

  **Streaming Support** (NEW):
  - Set `streaming=true` for large result sets
  - Returns results as NDJSON chunks for memory efficiency
  - Only available for read-only queries during direct execution
  - Bypasses queue for immediate streaming when system has capacity

  Credit consumption:
  - Variable based on query complexity: 1-50 credits
  - Simple MATCH queries: 1-5 credits
  - Complex aggregations/joins: 5-25 credits
  - Large result sets: 10-50 credits
  - Streaming queries: charged per 1000 rows streamed
  - Queued queries consume credits on completion

  Security features:
  - Role-based access control
  - Rate limiting based on subscription tier
  - Query timeout protection
  - Automatic load balancing

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      streaming (Union[Unset, bool]): Enable streaming response for large result sets (read-only
          queries only) Default: False.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CypherQueryRequest): Request model for Cypher query execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, CypherQueryResponse, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    body=body,
    streaming=streaming,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = client.get_httpx_client().request(
    **kwargs,
  )

  return _build_response(client=client, response=response)


def sync(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: CypherQueryRequest,
  streaming: Union[Unset, bool] = False,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Execute a Cypher query

   Execute a Cypher query against the specified graph database.

  Queries are automatically queued under heavy load for optimal performance.
  Write operations are allowed for users with appropriate permissions:
  - User graphs: member/admin role required
  - Shared repositories: read-only access only

  **Streaming Support** (NEW):
  - Set `streaming=true` for large result sets
  - Returns results as NDJSON chunks for memory efficiency
  - Only available for read-only queries during direct execution
  - Bypasses queue for immediate streaming when system has capacity

  Credit consumption:
  - Variable based on query complexity: 1-50 credits
  - Simple MATCH queries: 1-5 credits
  - Complex aggregations/joins: 5-25 credits
  - Large result sets: 10-50 credits
  - Streaming queries: charged per 1000 rows streamed
  - Queued queries consume credits on completion

  Security features:
  - Role-based access control
  - Rate limiting based on subscription tier
  - Query timeout protection
  - Automatic load balancing

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      streaming (Union[Unset, bool]): Enable streaming response for large result sets (read-only
          queries only) Default: False.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CypherQueryRequest): Request model for Cypher query execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, CypherQueryResponse, HTTPValidationError]
  """

  return sync_detailed(
    graph_id=graph_id,
    client=client,
    body=body,
    streaming=streaming,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: CypherQueryRequest,
  streaming: Union[Unset, bool] = False,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Execute a Cypher query

   Execute a Cypher query against the specified graph database.

  Queries are automatically queued under heavy load for optimal performance.
  Write operations are allowed for users with appropriate permissions:
  - User graphs: member/admin role required
  - Shared repositories: read-only access only

  **Streaming Support** (NEW):
  - Set `streaming=true` for large result sets
  - Returns results as NDJSON chunks for memory efficiency
  - Only available for read-only queries during direct execution
  - Bypasses queue for immediate streaming when system has capacity

  Credit consumption:
  - Variable based on query complexity: 1-50 credits
  - Simple MATCH queries: 1-5 credits
  - Complex aggregations/joins: 5-25 credits
  - Large result sets: 10-50 credits
  - Streaming queries: charged per 1000 rows streamed
  - Queued queries consume credits on completion

  Security features:
  - Role-based access control
  - Rate limiting based on subscription tier
  - Query timeout protection
  - Automatic load balancing

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      streaming (Union[Unset, bool]): Enable streaming response for large result sets (read-only
          queries only) Default: False.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CypherQueryRequest): Request model for Cypher query execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, CypherQueryResponse, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    body=body,
    streaming=streaming,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: CypherQueryRequest,
  streaming: Union[Unset, bool] = False,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, CypherQueryResponse, HTTPValidationError]]:
  """Execute a Cypher query

   Execute a Cypher query against the specified graph database.

  Queries are automatically queued under heavy load for optimal performance.
  Write operations are allowed for users with appropriate permissions:
  - User graphs: member/admin role required
  - Shared repositories: read-only access only

  **Streaming Support** (NEW):
  - Set `streaming=true` for large result sets
  - Returns results as NDJSON chunks for memory efficiency
  - Only available for read-only queries during direct execution
  - Bypasses queue for immediate streaming when system has capacity

  Credit consumption:
  - Variable based on query complexity: 1-50 credits
  - Simple MATCH queries: 1-5 credits
  - Complex aggregations/joins: 5-25 credits
  - Large result sets: 10-50 credits
  - Streaming queries: charged per 1000 rows streamed
  - Queued queries consume credits on completion

  Security features:
  - Role-based access control
  - Rate limiting based on subscription tier
  - Query timeout protection
  - Automatic load balancing

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      streaming (Union[Unset, bool]): Enable streaming response for large result sets (read-only
          queries only) Default: False.
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CypherQueryRequest): Request model for Cypher query execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, CypherQueryResponse, HTTPValidationError]
  """

  return (
    await asyncio_detailed(
      graph_id=graph_id,
      client=client,
      body=body,
      streaming=streaming,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
