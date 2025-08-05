from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.task_list_item import TaskListItem


T = TypeVar("T", bound="TaskListResponse")


@_attrs_define
class TaskListResponse:
  """Response model for task list.

  Attributes:
      tasks (list['TaskListItem']): List of user tasks
      total (int): Total number of tasks
      message (str): Informational message
      note (Union[None, Unset, str]): Additional notes or limitations
  """

  tasks: list["TaskListItem"]
  total: int
  message: str
  note: Union[None, Unset, str] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    tasks = []
    for tasks_item_data in self.tasks:
      tasks_item = tasks_item_data.to_dict()
      tasks.append(tasks_item)

    total = self.total

    message = self.message

    note: Union[None, Unset, str]
    if isinstance(self.note, Unset):
      note = UNSET
    else:
      note = self.note

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "tasks": tasks,
        "total": total,
        "message": message,
      }
    )
    if note is not UNSET:
      field_dict["note"] = note

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.task_list_item import TaskListItem

    d = dict(src_dict)
    tasks = []
    _tasks = d.pop("tasks")
    for tasks_item_data in _tasks:
      tasks_item = TaskListItem.from_dict(tasks_item_data)

      tasks.append(tasks_item)

    total = d.pop("total")

    message = d.pop("message")

    def _parse_note(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    note = _parse_note(d.pop("note", UNSET))

    task_list_response = cls(
      tasks=tasks,
      total=total,
      message=message,
      note=note,
    )

    task_list_response.additional_properties = d
    return task_list_response

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
