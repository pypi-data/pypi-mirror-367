from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.company_create import CompanyCreate
from ...models.company_response import CompanyResponse
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
  graph_id: str,
  *,
  body: CompanyCreate,
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
    "url": f"/v1/{graph_id}/company",
    "cookies": cookies,
  }

  _kwargs["json"] = body.to_dict()

  headers["Content-Type"] = "application/json"

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]:
  if response.status_code == 201:
    response_201 = CompanyResponse.from_dict(response.json())

    return response_201
  if response.status_code == 400:
    response_400 = ErrorResponse.from_dict(response.json())

    return response_400
  if response.status_code == 402:
    response_402 = ErrorResponse.from_dict(response.json())

    return response_402
  if response.status_code == 403:
    response_403 = ErrorResponse.from_dict(response.json())

    return response_403
  if response.status_code == 409:
    response_409 = ErrorResponse.from_dict(response.json())

    return response_409
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
) -> Response[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]:
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
  body: CompanyCreate,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]:
  """Create Company

   Create a new company in the specified graph.

  This endpoint creates a new company node with the provided information.
  The company identifier is auto-generated if not provided.

  Credit consumption:
  - Base cost: 5.0 credits
  - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Required fields:
  - name: Company name
  - uri: Company website URL

  Optional fields include CIK, EIN, SIC code, state of incorporation, etc.

  Args:
      graph_id (str): Graph database identifier where the company will be created
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CompanyCreate):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]
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
  body: CompanyCreate,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]:
  """Create Company

   Create a new company in the specified graph.

  This endpoint creates a new company node with the provided information.
  The company identifier is auto-generated if not provided.

  Credit consumption:
  - Base cost: 5.0 credits
  - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Required fields:
  - name: Company name
  - uri: Company website URL

  Optional fields include CIK, EIN, SIC code, state of incorporation, etc.

  Args:
      graph_id (str): Graph database identifier where the company will be created
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CompanyCreate):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[CompanyResponse, ErrorResponse, HTTPValidationError]
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
  body: CompanyCreate,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]:
  """Create Company

   Create a new company in the specified graph.

  This endpoint creates a new company node with the provided information.
  The company identifier is auto-generated if not provided.

  Credit consumption:
  - Base cost: 5.0 credits
  - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Required fields:
  - name: Company name
  - uri: Company website URL

  Optional fields include CIK, EIN, SIC code, state of incorporation, etc.

  Args:
      graph_id (str): Graph database identifier where the company will be created
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CompanyCreate):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]
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
  body: CompanyCreate,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[CompanyResponse, ErrorResponse, HTTPValidationError]]:
  """Create Company

   Create a new company in the specified graph.

  This endpoint creates a new company node with the provided information.
  The company identifier is auto-generated if not provided.

  Credit consumption:
  - Base cost: 5.0 credits
  - Multiplied by graph tier (standard=1x, enterprise=2x, premium=4x)

  Required fields:
  - name: Company name
  - uri: Company website URL

  Optional fields include CIK, EIN, SIC code, state of incorporation, etc.

  Args:
      graph_id (str): Graph database identifier where the company will be created
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (CompanyCreate):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[CompanyResponse, ErrorResponse, HTTPValidationError]
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
