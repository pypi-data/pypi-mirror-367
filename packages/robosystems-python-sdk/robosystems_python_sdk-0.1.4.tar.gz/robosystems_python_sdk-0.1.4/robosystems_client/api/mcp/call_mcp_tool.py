from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.mcp_tool_call import MCPToolCall
from ...models.mcp_tool_result import MCPToolResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
  *,
  body: MCPToolCall,
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
    "url": f"/v1/{graph_id}/mcp/call-tool",
    "cookies": cookies,
  }

  _kwargs["json"] = body.to_dict()

  headers["Content-Type"] = "application/json"

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]:
  if response.status_code == 200:
    response_200 = MCPToolResult.from_dict(response.json())

    return response_200
  if response.status_code == 400:
    response_400 = ErrorResponse.from_dict(response.json())

    return response_400
  if response.status_code == 402:
    response_402 = ErrorResponse.from_dict(response.json())

    return response_402
  if response.status_code == 403:
    response_403 = ErrorResponse.from_dict(response.json())

    return response_403
  if response.status_code == 408:
    response_408 = ErrorResponse.from_dict(response.json())

    return response_408
  if response.status_code == 500:
    response_500 = ErrorResponse.from_dict(response.json())

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
) -> Response[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]:
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
  body: MCPToolCall,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]:
  """Execute MCP Tool

   Execute an MCP tool with the given arguments.

      This endpoint provides access to Model Context Protocol (MCP) tools that can perform
      various graph operations and queries. Each tool execution consumes credits based on
      the tool type and complexity.

      Credit costs (tiered by operation complexity):
      - Simple operations (metadata, status): 2-15 credits
      - Schema operations (taxonomy, schema): 5-30 credits
      - Query operations (cypher, analysis): 10-75 credits
      - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (MCPToolCall): Request model for MCP tool execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    body=body,
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
  body: MCPToolCall,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]:
  """Execute MCP Tool

   Execute an MCP tool with the given arguments.

      This endpoint provides access to Model Context Protocol (MCP) tools that can perform
      various graph operations and queries. Each tool execution consumes credits based on
      the tool type and complexity.

      Credit costs (tiered by operation complexity):
      - Simple operations (metadata, status): 2-15 credits
      - Schema operations (taxonomy, schema): 5-30 credits
      - Query operations (cypher, analysis): 10-75 credits
      - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (MCPToolCall): Request model for MCP tool execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[ErrorResponse, HTTPValidationError, MCPToolResult]
  """

  return sync_detailed(
    graph_id=graph_id,
    client=client,
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: MCPToolCall,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]:
  """Execute MCP Tool

   Execute an MCP tool with the given arguments.

      This endpoint provides access to Model Context Protocol (MCP) tools that can perform
      various graph operations and queries. Each tool execution consumes credits based on
      the tool type and complexity.

      Credit costs (tiered by operation complexity):
      - Simple operations (metadata, status): 2-15 credits
      - Schema operations (taxonomy, schema): 5-30 credits
      - Query operations (cypher, analysis): 10-75 credits
      - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (MCPToolCall): Request model for MCP tool execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  body: MCPToolCall,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, MCPToolResult]]:
  """Execute MCP Tool

   Execute an MCP tool with the given arguments.

      This endpoint provides access to Model Context Protocol (MCP) tools that can perform
      various graph operations and queries. Each tool execution consumes credits based on
      the tool type and complexity.

      Credit costs (tiered by operation complexity):
      - Simple operations (metadata, status): 2-15 credits
      - Schema operations (taxonomy, schema): 5-30 credits
      - Query operations (cypher, analysis): 10-75 credits
      - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Args:
      graph_id (str): Graph database identifier (3-63 characters: letters, numbers, underscores;
          starts with letter)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (MCPToolCall): Request model for MCP tool execution.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[ErrorResponse, HTTPValidationError, MCPToolResult]
  """

  return (
    await asyncio_detailed(
      graph_id=graph_id,
      client=client,
      body=body,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
