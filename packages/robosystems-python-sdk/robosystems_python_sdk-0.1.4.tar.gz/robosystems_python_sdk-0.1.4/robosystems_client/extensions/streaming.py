"""Streaming support for Cypher query execution.

This module provides streaming functionality that extends the auto-generated SDK.
It won't be overwritten when the SDK is regenerated from the OpenAPI spec.
"""

import json
from http import HTTPStatus
from typing import AsyncIterator, Iterator, Union


from .. import errors
from ..client import AuthenticatedClient
from ..models.cypher_query_request import CypherQueryRequest
from ..types import UNSET, Unset


def _get_kwargs(
  graph_id: str,
  *,
  body: CypherQueryRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> dict:
  """Build request kwargs for streaming query."""
  headers = {}
  if not isinstance(authorization, Unset):
    headers["authorization"] = authorization

  cookies = {}
  if auth_token is not UNSET:
    cookies["auth-token"] = auth_token

  # Always enable streaming for this endpoint
  params = {"streaming": True}

  _kwargs = {
    "method": "post",
    "url": f"/v1/{graph_id}/graph/query",
    "params": params,
    "cookies": cookies,
    "json": body.to_dict(),
    "headers": {**headers, "Content-Type": "application/json"},
  }

  return _kwargs


def sync_streaming(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: CypherQueryRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Iterator[dict]:
  """Execute a Cypher query with streaming response (synchronous).

  Returns an iterator of parsed JSON chunks from the NDJSON stream.
  Each chunk contains:
  - data: List of result rows for this chunk
  - columns: Column names (included in first chunk)
  - row_count: Number of rows in this chunk
  - graph_id: Graph identifier
  - timestamp: ISO timestamp
  - final: True if this is the last chunk (includes execution_time_ms)

  Args:
      graph_id: Graph database identifier
      client: Authenticated client instance
      body: Cypher query request
      authorization: Optional authorization header
      auth_token: Optional auth token cookie

  Yields:
      dict: Parsed JSON chunks from the streaming response

  Raises:
      errors.UnexpectedStatus: If the server returns an error status
      httpx.TimeoutException: If the request times out
      json.JSONDecodeError: If a chunk is not valid JSON
  """
  kwargs = _get_kwargs(
    graph_id=graph_id,
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  # Use stream=True for chunked response
  with client.get_httpx_client().stream(**kwargs) as response:
    if response.status_code != HTTPStatus.OK:
      # Read full error response
      error_content = response.read()
      if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, error_content)
      return

    # Stream NDJSON chunks
    for line in response.iter_lines():
      if line:  # Skip empty lines
        try:
          chunk = json.loads(line)
          yield chunk
        except json.JSONDecodeError as e:
          # Log or handle decode error
          raise ValueError(f"Invalid JSON chunk: {line}") from e


async def asyncio_streaming(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: CypherQueryRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> AsyncIterator[dict]:
  """Execute a Cypher query with streaming response (asynchronous).

  Returns an async iterator of parsed JSON chunks from the NDJSON stream.
  Each chunk contains:
  - data: List of result rows for this chunk
  - columns: Column names (included in first chunk)
  - row_count: Number of rows in this chunk
  - graph_id: Graph identifier
  - timestamp: ISO timestamp
  - final: True if this is the last chunk (includes execution_time_ms)

  Args:
      graph_id: Graph database identifier
      client: Authenticated client instance
      body: Cypher query request
      authorization: Optional authorization header
      auth_token: Optional auth token cookie

  Yields:
      dict: Parsed JSON chunks from the streaming response

  Raises:
      errors.UnexpectedStatus: If the server returns an error status
      httpx.TimeoutException: If the request times out
      json.JSONDecodeError: If a chunk is not valid JSON

  Example:
      >>> async for chunk in asyncio_streaming(
      ...     graph_id="company_123",
      ...     client=client,
      ...     body=CypherQueryRequest(
      ...         query="MATCH (n:Company) RETURN n",
      ...         parameters={"limit": 10000}
      ...     )
      ... ):
      ...     print(f"Received {chunk['row_count']} rows")
      ...     for row in chunk['data']:
      ...         process_row(row)
  """
  kwargs = _get_kwargs(
    graph_id=graph_id,
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  # Use stream=True for chunked response
  async with client.get_async_httpx_client().stream(**kwargs) as response:
    if response.status_code != HTTPStatus.OK:
      # Read full error response
      error_content = await response.aread()
      if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, error_content)
      return

    # Stream NDJSON chunks
    async for line in response.aiter_lines():
      if line:  # Skip empty lines
        try:
          chunk = json.loads(line)
          yield chunk
        except json.JSONDecodeError as e:
          # Log or handle decode error
          raise ValueError(f"Invalid JSON chunk: {line}") from e
