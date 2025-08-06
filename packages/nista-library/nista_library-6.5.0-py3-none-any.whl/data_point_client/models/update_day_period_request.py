from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


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
  from ..models.day_data_by_hour_transfer import DayDataByHourTransfer





T = TypeVar("T", bound="UpdateDayPeriodRequest")


@attr.s(auto_attribs=True)
class UpdateDayPeriodRequest:
    """ 
        Attributes:
            execution_id (Union[Unset, None, str]):
            day_data (Union[Unset, None, DayDataByHourTransfer]):
            unit (Union[Unset, None, str]):
            date (Union[Unset, None, datetime.datetime]):
     """

    execution_id: Union[Unset, None, str] = UNSET
    day_data: Union[Unset, None, 'DayDataByHourTransfer'] = UNSET
    unit: Union[Unset, None, str] = UNSET
    date: Union[Unset, None, datetime.datetime] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.day_data_by_hour_transfer import DayDataByHourTransfer
        execution_id = self.execution_id
        day_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.day_data, Unset):
            day_data = self.day_data.to_dict() if self.day_data else None

        unit = self.unit
        date: Union[Unset, None, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat() if self.date else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if execution_id is not UNSET:
            field_dict["executionId"] = execution_id
        if day_data is not UNSET:
            field_dict["dayData"] = day_data
        if unit is not UNSET:
            field_dict["unit"] = unit
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.day_data_by_hour_transfer import DayDataByHourTransfer
        d = src_dict.copy()
        execution_id = d.pop("executionId", UNSET)

        _day_data = d.pop("dayData", UNSET)
        day_data: Union[Unset, None, DayDataByHourTransfer]
        if _day_data is None:
            day_data = None
        elif isinstance(_day_data,  Unset):
            day_data = UNSET
        else:
            day_data = DayDataByHourTransfer.from_dict(_day_data)




        unit = d.pop("unit", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, None, datetime.datetime]
        if _date is None:
            date = None
        elif isinstance(_date,  Unset):
            date = UNSET
        else:
            date = isoparse(_date)




        update_day_period_request = cls(
            execution_id=execution_id,
            day_data=day_data,
            unit=unit,
            date=date,
        )

        return update_day_period_request

