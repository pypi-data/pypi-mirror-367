from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CompanyCreate")


@_attrs_define
class CompanyCreate:
  """
  Attributes:
      name (str):
      uri (str):
      cik (Union[None, Unset, str]):
      database (Union[None, Unset, str]):
      sic (Union[None, Unset, str]):
      sic_description (Union[None, Unset, str]):
      category (Union[None, Unset, str]):
      state_of_incorporation (Union[None, Unset, str]):
      fiscal_year_end (Union[None, Unset, str]):
      ein (Union[None, Unset, str]):
      tier (Union[None, Unset, str]): Graph tier to create (standard, enterprise, premium). If not specified, defaults
          to standard. Example: standard.
      extensions (Union[None, Unset, list[str]]): Schema extensions to enable in the company graph. If not specified,
          base schema only will be loaded for stability. Available extensions: roboledger, roboinvestor, roboscm, robofo,
          robohrm, roboepm, roboreport Example: ['roboledger', 'roboinvestor'].
  """

  name: str
  uri: str
  cik: Union[None, Unset, str] = UNSET
  database: Union[None, Unset, str] = UNSET
  sic: Union[None, Unset, str] = UNSET
  sic_description: Union[None, Unset, str] = UNSET
  category: Union[None, Unset, str] = UNSET
  state_of_incorporation: Union[None, Unset, str] = UNSET
  fiscal_year_end: Union[None, Unset, str] = UNSET
  ein: Union[None, Unset, str] = UNSET
  tier: Union[None, Unset, str] = UNSET
  extensions: Union[None, Unset, list[str]] = UNSET
  additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

  def to_dict(self) -> dict[str, Any]:
    name = self.name

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

    tier: Union[None, Unset, str]
    if isinstance(self.tier, Unset):
      tier = UNSET
    else:
      tier = self.tier

    extensions: Union[None, Unset, list[str]]
    if isinstance(self.extensions, Unset):
      extensions = UNSET
    elif isinstance(self.extensions, list):
      extensions = self.extensions

    else:
      extensions = self.extensions

    field_dict: dict[str, Any] = {}
    field_dict.update(self.additional_properties)
    field_dict.update(
      {
        "name": name,
        "uri": uri,
      }
    )
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
    if tier is not UNSET:
      field_dict["tier"] = tier
    if extensions is not UNSET:
      field_dict["extensions"] = extensions

    return field_dict

  @classmethod
  def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
    d = dict(src_dict)
    name = d.pop("name")

    uri = d.pop("uri")

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

    def _parse_tier(data: object) -> Union[None, Unset, str]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      return cast(Union[None, Unset, str], data)

    tier = _parse_tier(d.pop("tier", UNSET))

    def _parse_extensions(data: object) -> Union[None, Unset, list[str]]:
      if data is None:
        return data
      if isinstance(data, Unset):
        return data
      try:
        if not isinstance(data, list):
          raise TypeError()
        extensions_type_0 = cast(list[str], data)

        return extensions_type_0
      except:  # noqa: E722
        pass
      return cast(Union[None, Unset, list[str]], data)

    extensions = _parse_extensions(d.pop("extensions", UNSET))

    company_create = cls(
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
      tier=tier,
      extensions=extensions,
    )

    company_create.additional_properties = d
    return company_create

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
