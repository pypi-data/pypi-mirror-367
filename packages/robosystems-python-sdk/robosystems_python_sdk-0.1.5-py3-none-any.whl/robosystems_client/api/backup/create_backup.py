from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.backup_create_request import BackupCreateRequest
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.task_response import TaskResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
  *,
  body: BackupCreateRequest,
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
    "url": f"/v1/{graph_id}/graph/backup/create",
    "cookies": cookies,
  }

  _kwargs["json"] = body.to_dict()

  headers["Content-Type"] = "application/json"

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, TaskResponse]]:
  if response.status_code == 202:
    response_202 = TaskResponse.from_dict(response.json())

    return response_202
  if response.status_code == 400:
    response_400 = ErrorResponse.from_dict(response.json())

    return response_400
  if response.status_code == 402:
    response_402 = ErrorResponse.from_dict(response.json())

    return response_402
  if response.status_code == 403:
    response_403 = ErrorResponse.from_dict(response.json())

    return response_403
  if response.status_code == 404:
    response_404 = ErrorResponse.from_dict(response.json())

    return response_404
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
) -> Response[Union[ErrorResponse, HTTPValidationError, TaskResponse]]:
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
  body: BackupCreateRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, TaskResponse]]:
  """Create Backup

   Create a backup of the graph database.

  Creates a complete backup of the Kuzu database (.kuzu file) with:
  - **Format**: Full database backup only (complete .kuzu file)
  - **Compression**: Always enabled for optimal storage
  - **Encryption**: Optional AES-256 encryption for security
  - **Retention**: Configurable retention period (1-2555 days)

  Backup features:
  - **Complete Backup**: Full database file backup
  - **Consistency**: Point-in-time consistent snapshot
  - **Download Support**: Unencrypted backups can be downloaded
  - **Restore Support**: Future support for encrypted backup restoration

  Important notes:
  - Only full_dump format is supported (no CSV/JSON exports)
  - Compression is always enabled
  - Encrypted backups cannot be downloaded (security measure)
  - All backups are stored securely in cloud storage

  Credit consumption:
  - Base cost: 25.0 credits
  - Large databases (>10GB): 50.0 credits
  - Multiplied by graph tier

  Returns a task ID for monitoring backup progress.

  Args:
      graph_id (str): Graph database identifier
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (BackupCreateRequest): Request model for creating a backup.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[ErrorResponse, HTTPValidationError, TaskResponse]]
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
  body: BackupCreateRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, TaskResponse]]:
  """Create Backup

   Create a backup of the graph database.

  Creates a complete backup of the Kuzu database (.kuzu file) with:
  - **Format**: Full database backup only (complete .kuzu file)
  - **Compression**: Always enabled for optimal storage
  - **Encryption**: Optional AES-256 encryption for security
  - **Retention**: Configurable retention period (1-2555 days)

  Backup features:
  - **Complete Backup**: Full database file backup
  - **Consistency**: Point-in-time consistent snapshot
  - **Download Support**: Unencrypted backups can be downloaded
  - **Restore Support**: Future support for encrypted backup restoration

  Important notes:
  - Only full_dump format is supported (no CSV/JSON exports)
  - Compression is always enabled
  - Encrypted backups cannot be downloaded (security measure)
  - All backups are stored securely in cloud storage

  Credit consumption:
  - Base cost: 25.0 credits
  - Large databases (>10GB): 50.0 credits
  - Multiplied by graph tier

  Returns a task ID for monitoring backup progress.

  Args:
      graph_id (str): Graph database identifier
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (BackupCreateRequest): Request model for creating a backup.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[ErrorResponse, HTTPValidationError, TaskResponse]
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
  body: BackupCreateRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, TaskResponse]]:
  """Create Backup

   Create a backup of the graph database.

  Creates a complete backup of the Kuzu database (.kuzu file) with:
  - **Format**: Full database backup only (complete .kuzu file)
  - **Compression**: Always enabled for optimal storage
  - **Encryption**: Optional AES-256 encryption for security
  - **Retention**: Configurable retention period (1-2555 days)

  Backup features:
  - **Complete Backup**: Full database file backup
  - **Consistency**: Point-in-time consistent snapshot
  - **Download Support**: Unencrypted backups can be downloaded
  - **Restore Support**: Future support for encrypted backup restoration

  Important notes:
  - Only full_dump format is supported (no CSV/JSON exports)
  - Compression is always enabled
  - Encrypted backups cannot be downloaded (security measure)
  - All backups are stored securely in cloud storage

  Credit consumption:
  - Base cost: 25.0 credits
  - Large databases (>10GB): 50.0 credits
  - Multiplied by graph tier

  Returns a task ID for monitoring backup progress.

  Args:
      graph_id (str): Graph database identifier
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (BackupCreateRequest): Request model for creating a backup.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[ErrorResponse, HTTPValidationError, TaskResponse]]
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
  body: BackupCreateRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, TaskResponse]]:
  """Create Backup

   Create a backup of the graph database.

  Creates a complete backup of the Kuzu database (.kuzu file) with:
  - **Format**: Full database backup only (complete .kuzu file)
  - **Compression**: Always enabled for optimal storage
  - **Encryption**: Optional AES-256 encryption for security
  - **Retention**: Configurable retention period (1-2555 days)

  Backup features:
  - **Complete Backup**: Full database file backup
  - **Consistency**: Point-in-time consistent snapshot
  - **Download Support**: Unencrypted backups can be downloaded
  - **Restore Support**: Future support for encrypted backup restoration

  Important notes:
  - Only full_dump format is supported (no CSV/JSON exports)
  - Compression is always enabled
  - Encrypted backups cannot be downloaded (security measure)
  - All backups are stored securely in cloud storage

  Credit consumption:
  - Base cost: 25.0 credits
  - Large databases (>10GB): 50.0 credits
  - Multiplied by graph tier

  Returns a task ID for monitoring backup progress.

  Args:
      graph_id (str): Graph database identifier
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (BackupCreateRequest): Request model for creating a backup.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[ErrorResponse, HTTPValidationError, TaskResponse]
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
