from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
  from ..models.mcp_tool_result_result import MCPToolResultResult


T = TypeVar("T", bound="MCPToolResult")


@_attrs_define
class MCPToolResult:
  """Response model for MCP tool execution result.

  Attributes:
      result (MCPToolResultResult): Result of the MCP tool execution
  """

  result: "MCPToolResultResult"
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    result = self.result.to_dict()

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "result": result,
      }
    )

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.mcp_tool_result_result import MCPToolResultResult

    d = dict(src_dict)
    result = MCPToolResultResult.from_dict(d.pop("result"))

    mcp_tool_result = cls(
      result=result,
    )

    mcp_tool_result.additional_properties = d
    return mcp_tool_result

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
