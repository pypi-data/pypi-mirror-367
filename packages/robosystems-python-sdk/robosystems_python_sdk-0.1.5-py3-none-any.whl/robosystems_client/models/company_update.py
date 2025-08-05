from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CompanyUpdate")


@_attrs_define
class CompanyUpdate:
  """
  Attributes:
      name (Union[None, Unset, str]):
      uri (Union[None, Unset, str]):
      cik (Union[None, Unset, str]):
      database (Union[None, Unset, str]):
      sic (Union[None, Unset, str]):
      sic_description (Union[None, Unset, str]):
      category (Union[None, Unset, str]):
      state_of_incorporation (Union[None, Unset, str]):
      fiscal_year_end (Union[None, Unset, str]):
      ein (Union[None, Unset, str]):
  """

  name: Union[None, Unset, str] = UNSET
  uri: Union[None, Unset, str] = UNSET
  cik: Union[None, Unset, str] = UNSET
  database: Union[None, Unset, str] = UNSET
  sic: Union[None, Unset, str] = UNSET
  sic_description: Union[None, Unset, str] = UNSET
  category: Union[None, Unset, str] = UNSET
  state_of_incorporation: Union[None, Unset, str] = UNSET
  fiscal_year_end: Union[None, Unset, str] = UNSET
  ein: Union[None, Unset, str] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    name: Union[None, Unset, str]
    if isinstance(self.name, Unset):
      name = UNSET
    else:
      name = self.name

    uri: Union[None, Unset, str]
    if isinstance(self.uri, Unset):
      uri = UNSET
    else:
      uri = self.uri

    cik: Union[None, Unset, str]
    if isinstance(self.cik, Unset):
      cik = UNSET
    else:
      cik = self.cik

    database: Union[None, Unset, str]
    if isinstance(self.database, Unset):
      database = UNSET
    else:
      database = self.database

    sic: Union[None, Unset, str]
    if isinstance(self.sic, Unset):
      sic = UNSET
    else:
      sic = self.sic

    sic_description: Union[None, Unset, str]
    if isinstance(self.sic_description, Unset):
      sic_description = UNSET
    else:
      sic_description = self.sic_description

    category: Union[None, Unset, str]
    if isinstance(self.category, Unset):
      category = UNSET
    else:
      category = self.category

    state_of_incorporation: Union[None, Unset, str]
    if isinstance(self.state_of_incorporation, Unset):
      state_of_incorporation = UNSET
    else:
      state_of_incorporation = self.state_of_incorporation

    fiscal_year_end: Union[None, Unset, str]
    if isinstance(self.fiscal_year_end, Unset):
      fiscal_year_end = UNSET
    else:
      fiscal_year_end = self.fiscal_year_end

    ein: Union[None, Unset, str]
    if isinstance(self.ein, Unset):
      ein = UNSET
    else:
      ein = self.ein

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update({})
    if name is not UNSET:
      field_dict["name"] = name
    if uri is not UNSET:
      field_dict["uri"] = uri
    if cik is not UNSET:
      field_dict["cik"] = cik
    if database is not UNSET:
      field_dict["database"] = database
    if sic is not UNSET:
      field_dict["sic"] = sic
    if sic_description is not UNSET:
      field_dict["sic_description"] = sic_description
    if category is not UNSET:
      field_dict["category"] = category
    if state_of_incorporation is not UNSET:
      field_dict["state_of_incorporation"] = state_of_incorporation
    if fiscal_year_end is not UNSET:
      field_dict["fiscal_year_end"] = fiscal_year_end
    if ein is not UNSET:
      field_dict["ein"] = ein

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    d = dict(src_dict)

    def _parse_name(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    name = _parse_name(d.pop("name", UNSET))

    def _parse_uri(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    uri = _parse_uri(d.pop("uri", UNSET))

    def _parse_cik(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    cik = _parse_cik(d.pop("cik", UNSET))

    def _parse_database(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    database = _parse_database(d.pop("database", UNSET))

    def _parse_sic(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    sic = _parse_sic(d.pop("sic", UNSET))

    def _parse_sic_description(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    sic_description = _parse_sic_description(d.pop("sic_description", UNSET))

    def _parse_category(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    category = _parse_category(d.pop("category", UNSET))

    def _parse_state_of_incorporation(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    state_of_incorporation = _parse_state_of_incorporation(
      d.pop("state_of_incorporation", UNSET)
    )

    def _parse_fiscal_year_end(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    fiscal_year_end = _parse_fiscal_year_end(d.pop("fiscal_year_end", UNSET))

    def _parse_ein(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    ein = _parse_ein(d.pop("ein", UNSET))

    company_update = cls(
      name=name,
      uri=uri,
      cik=cik,
      database=database,
      sic=sic,
      sic_description=sic_description,
      category=category,
      state_of_incorporation=state_of_incorporation,
      fiscal_year_end=fiscal_year_end,
      ein=ein,
    )

    company_update.additional_properties = d
    return company_update

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
