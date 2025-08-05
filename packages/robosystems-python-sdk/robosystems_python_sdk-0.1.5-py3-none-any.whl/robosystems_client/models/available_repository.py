from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.repository_plan_info import RepositoryPlanInfo


T = TypeVar("T", bound="AvailableRepository")


@_attrs_define
class AvailableRepository:
  """Available shared repository information.

  Attributes:
      type_ (str): Repository type identifier
      name (str): Display name of the repository
      description (str): Repository description
      enabled (bool): Whether repository is available for subscription
      plans (list['RepositoryPlanInfo']): Available repository plans
      coming_soon (Union[None, Unset, bool]): Whether repository is coming soon Default: False.
  """

  type_: str
  name: str
  description: str
  enabled: bool
  plans: list["RepositoryPlanInfo"]
  coming_soon: Union[None, Unset, bool] = False
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    type_ = self.type_

    name = self.name

    description = self.description

    enabled = self.enabled

    plans = []
    for plans_item_data in self.plans:
      plans_item = plans_item_data.to_dict()
      plans.append(plans_item)

    coming_soon: Union[None, Unset, bool]
    if isinstance(self.coming_soon, Unset):
      coming_soon = UNSET
    else:
      coming_soon = self.coming_soon

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "type": type_,
        "name": name,
        "description": description,
        "enabled": enabled,
        "plans": plans,
      }
    )
    if coming_soon is not UNSET:
      field_dict["coming_soon"] = coming_soon

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.repository_plan_info import RepositoryPlanInfo

    d = dict(src_dict)
    type_ = d.pop("type")

    name = d.pop("name")

    description = d.pop("description")

    enabled = d.pop("enabled")

    plans = []
    _plans = d.pop("plans")
    for plans_item_data in _plans:
      plans_item = RepositoryPlanInfo.from_dict(plans_item_data)

      plans.append(plans_item)

    def _parse_coming_soon(data: object) -> Union[None, Unset, bool]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, bool], data)

    coming_soon = _parse_coming_soon(d.pop("coming_soon", UNSET))

    available_repository = cls(
      type_=type_,
      name=name,
      description=description,
      enabled=enabled,
      plans=plans,
      coming_soon=coming_soon,
    )

    available_repository.additional_properties = d
    return available_repository

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
