from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.available_extensions_response import AvailableExtensionsResponse
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
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
    "method": "get",
    "url": f"/v1/{graph_id}/company/extensions",
    "cookies": cookies,
  }

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]:
  if response.status_code == 200:
    response_200 = AvailableExtensionsResponse.from_dict(response.json())

    return response_200
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
) -> Response[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]:
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
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]:
  """List Available Extensions

   Get available schema extensions for creating company graphs.

  This endpoint provides information about available schema extensions that can be
  selected when creating a new company graph. Extensions add specialized functionality:

  - **RoboLedger**: Financial reporting and accounting capabilities
  - **RoboInvestor**: Investment portfolio management
  - **RoboSCM**: Supply chain and inventory management
  - **RoboHRM**: Human resources and payroll
  - **RoboEPM**: Enterprise performance management
  - **RoboReport**: Regulatory filing automation
  - **RoboFO**: CRM and sales pipeline management

  The base schema is always included and provides core business entities.

  Args:
      graph_id (str): Graph ID (not used for this endpoint)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
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
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]:
  """List Available Extensions

   Get available schema extensions for creating company graphs.

  This endpoint provides information about available schema extensions that can be
  selected when creating a new company graph. Extensions add specialized functionality:

  - **RoboLedger**: Financial reporting and accounting capabilities
  - **RoboInvestor**: Investment portfolio management
  - **RoboSCM**: Supply chain and inventory management
  - **RoboHRM**: Human resources and payroll
  - **RoboEPM**: Enterprise performance management
  - **RoboReport**: Regulatory filing automation
  - **RoboFO**: CRM and sales pipeline management

  The base schema is always included and provides core business entities.

  Args:
      graph_id (str): Graph ID (not used for this endpoint)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]
  """

  return sync_detailed(
    graph_id=graph_id,
    client=client,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]:
  """List Available Extensions

   Get available schema extensions for creating company graphs.

  This endpoint provides information about available schema extensions that can be
  selected when creating a new company graph. Extensions add specialized functionality:

  - **RoboLedger**: Financial reporting and accounting capabilities
  - **RoboInvestor**: Investment portfolio management
  - **RoboSCM**: Supply chain and inventory management
  - **RoboHRM**: Human resources and payroll
  - **RoboEPM**: Enterprise performance management
  - **RoboReport**: Regulatory filing automation
  - **RoboFO**: CRM and sales pipeline management

  The base schema is always included and provides core business entities.

  Args:
      graph_id (str): Graph ID (not used for this endpoint)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    graph_id=graph_id,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  graph_id: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]]:
  """List Available Extensions

   Get available schema extensions for creating company graphs.

  This endpoint provides information about available schema extensions that can be
  selected when creating a new company graph. Extensions add specialized functionality:

  - **RoboLedger**: Financial reporting and accounting capabilities
  - **RoboInvestor**: Investment portfolio management
  - **RoboSCM**: Supply chain and inventory management
  - **RoboHRM**: Human resources and payroll
  - **RoboEPM**: Enterprise performance management
  - **RoboReport**: Regulatory filing automation
  - **RoboFO**: CRM and sales pipeline management

  The base schema is always included and provides core business entities.

  Args:
      graph_id (str): Graph ID (not used for this endpoint)
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[AvailableExtensionsResponse, ErrorResponse, HTTPValidationError]
  """

  return (
    await asyncio_detailed(
      graph_id=graph_id,
      client=client,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
