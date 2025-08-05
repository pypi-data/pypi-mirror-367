from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.task_status_response_details_type_0 import (
    TaskStatusResponseDetailsType0,
  )


T = TypeVar("T", bound="TaskStatusResponse")


@_attrs_define
class TaskStatusResponse:
  """Response model for task status information.

  Attributes:
      task_id (str): Unique task identifier
      status (str): Current task status (pending, in_progress, completed, failed, retrying, cancelled)
      message (str): Human-readable status message
      progress (Union[None, Unset, float]): Task progress percentage (0-100)
      step (Union[None, Unset, str]): Current processing step
      details (Union['TaskStatusResponseDetailsType0', None, Unset]): Additional task-specific details
      result (Union[Any, None, Unset]): Task result (only present when completed)
      error (Union[None, Unset, str]): Error message (only present when failed)
      retry_count (Union[None, Unset, int]): Current retry attempt (only present when retrying)
      max_retries (Union[None, Unset, int]): Maximum retry attempts (only present when retrying)
  """

  task_id: str
  status: str
  message: str
  progress: Union[None, Unset, float] = UNSET
  step: Union[None, Unset, str] = UNSET
  details: Union["TaskStatusResponseDetailsType0", None, Unset] = UNSET
  result: Union[Any, None, Unset] = UNSET
  error: Union[None, Unset, str] = UNSET
  retry_count: Union[None, Unset, int] = UNSET
  max_retries: Union[None, Unset, int] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    from ..models.task_status_response_details_type_0 import (
      TaskStatusResponseDetailsType0,
    )

    task_id = self.task_id

    status = self.status

    message = self.message

    progress: Union[None, Unset, float]
    if isinstance(self.progress, Unset):
      progress = UNSET
    else:
      progress = self.progress

    step: Union[None, Unset, str]
    if isinstance(self.step, Unset):
      step = UNSET
    else:
      step = self.step

    details: Union[None, Unset, dict[str, Any]]
    if isinstance(self.details, Unset):
      details = UNSET
    elif isinstance(self.details, TaskStatusResponseDetailsType0):
      details = self.details.to_dict()
    else:
      details = self.details

    result: Union[Any, None, Unset]
    if isinstance(self.result, Unset):
      result = UNSET
    else:
      result = self.result

    error: Union[None, Unset, str]
    if isinstance(self.error, Unset):
      error = UNSET
    else:
      error = self.error

    retry_count: Union[None, Unset, int]
    if isinstance(self.retry_count, Unset):
      retry_count = UNSET
    else:
      retry_count = self.retry_count

    max_retries: Union[None, Unset, int]
    if isinstance(self.max_retries, Unset):
      max_retries = UNSET
    else:
      max_retries = self.max_retries

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "task_id": task_id,
        "status": status,
        "message": message,
      }
    )
    if progress is not UNSET:
      field_dict["progress"] = progress
    if step is not UNSET:
      field_dict["step"] = step
    if details is not UNSET:
      field_dict["details"] = details
    if result is not UNSET:
      field_dict["result"] = result
    if error is not UNSET:
      field_dict["error"] = error
    if retry_count is not UNSET:
      field_dict["retry_count"] = retry_count
    if max_retries is not UNSET:
      field_dict["max_retries"] = max_retries

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.task_status_response_details_type_0 import (
      TaskStatusResponseDetailsType0,
    )

    d = dict(src_dict)
    task_id = d.pop("task_id")

    status = d.pop("status")

    message = d.pop("message")

    def _parse_progress(data: object) -> Union[None, Unset, float]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, float], data)

    progress = _parse_progress(d.pop("progress", UNSET))

    def _parse_step(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    step = _parse_step(d.pop("step", UNSET))

    def _parse_details(
      data: object,
    ) -> Union["TaskStatusResponseDetailsType0", None, Unset]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      try:
        if not isinstance(data, dict):
          raise TypeError()
        details_type_0 = TaskStatusResponseDetailsType0.from_dict(data)

        return details_type_0
      except:  # noqa: E722
        pass
      return cast(Union["TaskStatusResponseDetailsType0", None, Unset], data)

    details = _parse_details(d.pop("details", UNSET))

    def _parse_result(data: object) -> Union[Any, None, Unset]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[Any, None, Unset], data)

    result = _parse_result(d.pop("result", UNSET))

    def _parse_error(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    error = _parse_error(d.pop("error", UNSET))

    def _parse_retry_count(data: object) -> Union[None, Unset, int]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, int], data)

    retry_count = _parse_retry_count(d.pop("retry_count", UNSET))

    def _parse_max_retries(data: object) -> Union[None, Unset, int]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, int], data)

    max_retries = _parse_max_retries(d.pop("max_retries", UNSET))

    task_status_response = cls(
      task_id=task_id,
      status=status,
      message=message,
      progress=progress,
      step=step,
      details=details,
      result=result,
      error=error,
      retry_count=retry_count,
      max_retries=max_retries,
    )

    task_status_response.additional_properties = d
    return task_status_response

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
