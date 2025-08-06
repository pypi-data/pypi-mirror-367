from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
import datetime
from typing import Union
from dateutil.parser import isoparse
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.gnista_unit_response import GnistaUnitResponse
  from ..models.day_data_base_transfer import DayDataBaseTransfer





T = TypeVar("T", bound="GetDayPeriodResponse")


@attr.s(auto_attribs=True)
class GetDayPeriodResponse:
    """ 
        Attributes:
            discriminator (str):
            day_data (Union[Unset, None, DayDataBaseTransfer]):
            date (Union[Unset, None, datetime.datetime]):
            unit (Union[Unset, None, GnistaUnitResponse]):
     """

    discriminator: str
    day_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    date: Union[Unset, None, datetime.datetime] = UNSET
    unit: Union[Unset, None, 'GnistaUnitResponse'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.day_data_base_transfer import DayDataBaseTransfer
        discriminator = self.discriminator
        day_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.day_data, Unset):
            day_data = self.day_data.to_dict() if self.day_data else None

        date: Union[Unset, None, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat() if self.date else None

        unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.unit, Unset):
            unit = self.unit.to_dict() if self.unit else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if day_data is not UNSET:
            field_dict["dayData"] = day_data
        if date is not UNSET:
            field_dict["date"] = date
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.day_data_base_transfer import DayDataBaseTransfer
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _day_data = d.pop("dayData", UNSET)
        day_data: Union[Unset, None, DayDataBaseTransfer]
        if _day_data is None:
            day_data = None
        elif isinstance(_day_data,  Unset):
            day_data = UNSET
        else:
            day_data = DayDataBaseTransfer.from_dict(_day_data)




        _date = d.pop("date", UNSET)
        date: Union[Unset, None, datetime.datetime]
        if _date is None:
            date = None
        elif isinstance(_date,  Unset):
            date = UNSET
        else:
            date = isoparse(_date)




        _unit = d.pop("unit", UNSET)
        unit: Union[Unset, None, GnistaUnitResponse]
        if _unit is None:
            unit = None
        elif isinstance(_unit,  Unset):
            unit = UNSET
        else:
            unit = GnistaUnitResponse.from_dict(_unit)




        get_day_period_response = cls(
            discriminator=discriminator,
            day_data=day_data,
            date=date,
            unit=unit,
        )

        get_day_period_response.additional_properties = d
        return get_day_period_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
