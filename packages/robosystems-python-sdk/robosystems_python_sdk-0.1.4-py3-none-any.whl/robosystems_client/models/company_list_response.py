from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
  from ..models.company_response import CompanyResponse


T = TypeVar("T", bound="CompanyListResponse")


@_attrs_define
class CompanyListResponse:
  """
  Attributes:
      companies (list['CompanyResponse']):
      total (int):
      limit (int):
      offset (int):
  """

  companies: list["CompanyResponse"]
  total: int
  limit: int
  offset: int
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    companies = []
    for companies_item_data in self.companies:
      companies_item = companies_item_data.to_dict()
      companies.append(companies_item)

    total = self.total

    limit = self.limit

    offset = self.offset

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "companies": companies,
        "total": total,
        "limit": limit,
        "offset": offset,
      }
    )

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    from ..models.company_response import CompanyResponse

    d = dict(src_dict)
    companies = []
    _companies = d.pop("companies")
    for companies_item_data in _companies:
      companies_item = CompanyResponse.from_dict(companies_item_data)

      companies.append(companies_item)

    total = d.pop("total")

    limit = d.pop("limit")

    offset = d.pop("offset")

    company_list_response = cls(
      companies=companies,
      total=total,
      limit=limit,
      offset=offset,
    )

    company_list_response.additional_properties = d
    return company_list_response

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
