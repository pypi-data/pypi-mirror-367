from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RepositoryPlanInfo")


@_attrs_define
class RepositoryPlanInfo:
  """Information about a repository plan.

  Attributes:
      plan (str): Repository plan name
      name (str): Display name of the tier
      monthly_price (float): Monthly price in USD
      monthly_credits (int): Monthly credit allocation
      features (list[str]): List of features included
  """

  plan: str
  name: str
  monthly_price: float
  monthly_credits: int
  features: list[str]
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    plan = self.plan

    name = self.name

    monthly_price = self.monthly_price

    monthly_credits = self.monthly_credits

    features = self.features

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "plan": plan,
        "name": name,
        "monthly_price": monthly_price,
        "monthly_credits": monthly_credits,
        "features": features,
      }
    )

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    d = dict(src_dict)
    plan = d.pop("plan")

    name = d.pop("name")

    monthly_price = d.pop("monthly_price")

    monthly_credits = d.pop("monthly_credits")

    features = cast(list[str], d.pop("features"))

    repository_plan_info = cls(
      plan=plan,
      name=name,
      monthly_price=monthly_price,
      monthly_credits=monthly_credits,
      features=features,
    )

    repository_plan_info.additional_properties = d
    return repository_plan_info

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
