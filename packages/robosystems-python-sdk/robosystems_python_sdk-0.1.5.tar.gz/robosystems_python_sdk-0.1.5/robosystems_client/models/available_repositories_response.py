from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
  from ..models.available_repository import AvailableRepository


T = TypeVar("T", bound="AvailableRepositoriesResponse")


@_attrs_define
class AvailableRepositoriesResponse:
  """Response for available shared repositories.

  Attributes:
      available_repositories (list['AvailableRepository']): List of available repositories
      total_types (int): Total number of repository types
  """

  available_repositories: list["AvailableRepository"]
  total_types: int
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    available_repositories = []
    for available_repositories_item_data in self.available_repositories:
      available_repositories_item = available_repositories_item_data.to_dict()
      available_repositories.append(available_repositories_item)

    total_types = self.total_types

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "available_repositories": available_repositories,
        "total_types": total_types,
      }
    )

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.available_repository import AvailableRepository

    d = dict(src_dict)
    available_repositories = []
    _available_repositories = d.pop("available_repositories")
    for available_repositories_item_data in _available_repositories:
      available_repositories_item = AvailableRepository.from_dict(
        available_repositories_item_data
      )

      available_repositories.append(available_repositories_item)

    total_types = d.pop("total_types")

    available_repositories_response = cls(
      available_repositories=available_repositories,
      total_types=total_types,
    )

    available_repositories_response.additional_properties = d
    return available_repositories_response

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
