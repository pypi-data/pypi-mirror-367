from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.custom_schema_definition import CustomSchemaDefinition
  from ..models.graph_metadata import GraphMetadata


T = TypeVar("T", bound="CreateGraphRequest")


@_attrs_define
class CreateGraphRequest:
  """Request model for creating a new graph.

  Attributes:
      metadata (GraphMetadata): Metadata for graph creation.
      instance_tier (Union[Unset, str]): Instance tier: standard, enterprise, or premium Default: 'standard'. Example:
          standard.
      custom_schema (Union['CustomSchemaDefinition', None, Unset]): Optional custom schema definition. If provided,
          overrides schema_extensions
  """

  metadata: "GraphMetadata"
  instance_tier: Union[Unset, str] = "standard"
  custom_schema: Union["CustomSchemaDefinition", None, Unset] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    from ..models.custom_schema_definition import CustomSchemaDefinition

    metadata = self.metadata.to_dict()

    instance_tier = self.instance_tier

    custom_schema: Union[None, Unset, dict[str, Any]]
    if isinstance(self.custom_schema, Unset):
      custom_schema = UNSET
    elif isinstance(self.custom_schema, CustomSchemaDefinition):
      custom_schema = self.custom_schema.to_dict()
    else:
      custom_schema = self.custom_schema

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "metadata": metadata,
      }
    )
    if instance_tier is not UNSET:
      field_dict["instance_tier"] = instance_tier
    if custom_schema is not UNSET:
      field_dict["custom_schema"] = custom_schema

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.custom_schema_definition import CustomSchemaDefinition
    from ..models.graph_metadata import GraphMetadata

    d = dict(src_dict)
    metadata = GraphMetadata.from_dict(d.pop("metadata"))

    instance_tier = d.pop("instance_tier", UNSET)

    def _parse_custom_schema(
      data: object,
    ) -> Union["CustomSchemaDefinition", None, Unset]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      try:
        if not isinstance(data, dict):
          raise TypeError()
        custom_schema_type_0 = CustomSchemaDefinition.from_dict(data)

        return custom_schema_type_0
      except:  # noqa: E722
        pass
      return cast(Union["CustomSchemaDefinition", None, Unset], data)

    custom_schema = _parse_custom_schema(d.pop("custom_schema", UNSET))

    create_graph_request = cls(
      metadata=metadata,
      instance_tier=instance_tier,
      custom_schema=custom_schema,
    )

    create_graph_request.additional_properties = d
    return create_graph_request

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
