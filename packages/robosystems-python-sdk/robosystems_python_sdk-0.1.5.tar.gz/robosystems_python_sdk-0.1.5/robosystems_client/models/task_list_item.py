from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskListItem")


@_attrs_define
class TaskListItem:
  """Individual task item in task list.

  Attributes:
      task_id (str): Unique task identifier
      status (str): Current task status
      created_at (Union[None, Unset, str]): Task creation timestamp
      task_type (Union[None, Unset, str]): Type of task
      progress (Union[None, Unset, float]): Task progress percentage
  """

  task_id: str
  status: str
  created_at: Union[None, Unset, str] = UNSET
  task_type: Union[None, Unset, str] = UNSET
  progress: Union[None, Unset, float] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    task_id = self.task_id

    status = self.status

    created_at: Union[None, Unset, str]
    if isinstance(self.created_at, Unset):
      created_at = UNSET
    else:
      created_at = self.created_at

    task_type: Union[None, Unset, str]
    if isinstance(self.task_type, Unset):
      task_type = UNSET
    else:
      task_type = self.task_type

    progress: Union[None, Unset, float]
    if isinstance(self.progress, Unset):
      progress = UNSET
    else:
      progress = self.progress

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "task_id": task_id,
        "status": status,
      }
    )
    if created_at is not UNSET:
      field_dict["created_at"] = created_at
    if task_type is not UNSET:
      field_dict["task_type"] = task_type
    if progress is not UNSET:
      field_dict["progress"] = progress

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    d = dict(src_dict)
    task_id = d.pop("task_id")

    status = d.pop("status")

    def _parse_created_at(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    created_at = _parse_created_at(d.pop("created_at", UNSET))

    def _parse_task_type(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    task_type = _parse_task_type(d.pop("task_type", UNSET))

    def _parse_progress(data: object) -> Union[None, Unset, float]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, float], data)

    progress = _parse_progress(d.pop("progress", UNSET))

    task_list_item = cls(
      task_id=task_id,
      status=status,
      created_at=created_at,
      task_type=task_type,
      progress=progress,
    )

    task_list_item.additional_properties = d
    return task_list_item

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
