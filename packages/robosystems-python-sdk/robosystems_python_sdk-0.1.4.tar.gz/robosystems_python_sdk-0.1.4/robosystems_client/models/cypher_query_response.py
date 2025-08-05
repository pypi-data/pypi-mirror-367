from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.cypher_query_response_data_type_0_item import (
    CypherQueryResponseDataType0Item,
  )


T = TypeVar("T", bound="CypherQueryResponse")


@_attrs_define
class CypherQueryResponse:
  """Response model for Cypher query results.

  Attributes:
      success (bool): Whether the query executed successfully
      row_count (int): Number of rows returned
      execution_time_ms (float): Query execution time in milliseconds
      graph_id (str): Graph database identifier
      timestamp (str): Query execution timestamp
      data (Union[None, Unset, list['CypherQueryResponseDataType0Item']]): Query results as a list of dictionaries
      columns (Union[None, Unset, list[str]]): Column names from the query result
      error (Union[None, Unset, str]): Error message if query failed
  """

  success: bool
  row_count: int
  execution_time_ms: float
  graph_id: str
  timestamp: str
  data: Union[None, Unset, list["CypherQueryResponseDataType0Item"]] = UNSET
  columns: Union[None, Unset, list[str]] = UNSET
  error: Union[None, Unset, str] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    success = self.success

    row_count = self.row_count

    execution_time_ms = self.execution_time_ms

    graph_id = self.graph_id

    timestamp = self.timestamp

    data: Union[None, Unset, list[dict[str, Any]]]
    if isinstance(self.data, Unset):
      data = UNSET
    elif isinstance(self.data, list):
      data = []
      for data_type_0_item_data in self.data:
        data_type_0_item = data_type_0_item_data.to_dict()
        data.append(data_type_0_item)

    else:
      data = self.data

    columns: Union[None, Unset, list[str]]
    if isinstance(self.columns, Unset):
      columns = UNSET
    elif isinstance(self.columns, list):
      columns = self.columns

    else:
      columns = self.columns

    error: Union[None, Unset, str]
    if isinstance(self.error, Unset):
      error = UNSET
    else:
      error = self.error

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "success": success,
        "row_count": row_count,
        "execution_time_ms": execution_time_ms,
        "graph_id": graph_id,
        "timestamp": timestamp,
      }
    )
    if data is not UNSET:
      field_dict["data"] = data
    if columns is not UNSET:
      field_dict["columns"] = columns
    if error is not UNSET:
      field_dict["error"] = error

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.cypher_query_response_data_type_0_item import (
      CypherQueryResponseDataType0Item,
    )

    d = dict(src_dict)
    success = d.pop("success")

    row_count = d.pop("row_count")

    execution_time_ms = d.pop("execution_time_ms")

    graph_id = d.pop("graph_id")

    timestamp = d.pop("timestamp")

    def _parse_data(
      data: object,
    ) -> Union[None, Unset, list["CypherQueryResponseDataType0Item"]]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      try:
        if not isinstance(data, list):
          raise TypeError()
        data_type_0 = []
        _data_type_0 = data
        for data_type_0_item_data in _data_type_0:
          data_type_0_item = CypherQueryResponseDataType0Item.from_dict(
            data_type_0_item_data
          )

          data_type_0.append(data_type_0_item)

        return data_type_0
      except:  # noqa: E722
        pass
      return cast(Union[None, Unset, list["CypherQueryResponseDataType0Item"]], data)

    data = _parse_data(d.pop("data", UNSET))

    def _parse_columns(data: object) -> Union[None, Unset, list[str]]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      try:
        if not isinstance(data, list):
          raise TypeError()
        columns_type_0 = cast(list[str], data)

        return columns_type_0
      except:  # noqa: E722
        pass
      return cast(Union[None, Unset, list[str]], data)

    columns = _parse_columns(d.pop("columns", UNSET))

    def _parse_error(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    error = _parse_error(d.pop("error", UNSET))

    cypher_query_response = cls(
      success=success,
      row_count=row_count,
      execution_time_ms=execution_time_ms,
      graph_id=graph_id,
      timestamp=timestamp,
      data=data,
      columns=columns,
      error=error,
    )

    cypher_query_response.additional_properties = d
    return cypher_query_response

  @property
  def additional_keys(self) -> list[str]:
    return list(self.additional_properties.keys())

  def __getitem__(self, key: str) -> Any:
    return self.additional_properties[key]

  def __setitem__(self, key: str, value: Any) -> None:
    self.additional_properties[key] = value

  def __delitem__(self, key: str) -> None:
    del self.additional_properties[key]

  def __contains__(self, key: str) -> bool:
    return key in self.additional_properties
