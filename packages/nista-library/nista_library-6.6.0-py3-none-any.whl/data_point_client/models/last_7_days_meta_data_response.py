from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

import datetime
from typing import Dict
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import Union
from typing import cast
from typing import Optional

if TYPE_CHECKING:
  from ..models.week_meta_data_response import WeekMetaDataResponse





T = TypeVar("T", bound="Last7DaysMetaDataResponse")


@attr.s(auto_attribs=True)
class Last7DaysMetaDataResponse:
    """ 
        Attributes:
            current_week (Union[Unset, None, WeekMetaDataResponse]):
            comparison_week (Union[Unset, None, WeekMetaDataResponse]):
            average_week (Union[Unset, None, WeekMetaDataResponse]):
            start (Union[Unset, None, datetime.date]):
            end (Union[Unset, None, datetime.date]):
            unit (Union[Unset, None, str]):
     """

    current_week: Union[Unset, None, 'WeekMetaDataResponse'] = UNSET
    comparison_week: Union[Unset, None, 'WeekMetaDataResponse'] = UNSET
    average_week: Union[Unset, None, 'WeekMetaDataResponse'] = UNSET
    start: Union[Unset, None, datetime.date] = UNSET
    end: Union[Unset, None, datetime.date] = UNSET
    unit: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.week_meta_data_response import WeekMetaDataResponse
        current_week: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.current_week, Unset):
            current_week = self.current_week.to_dict() if self.current_week else None

        comparison_week: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.comparison_week, Unset):
            comparison_week = self.comparison_week.to_dict() if self.comparison_week else None

        average_week: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.average_week, Unset):
            average_week = self.average_week.to_dict() if self.average_week else None

        start: Union[Unset, None, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat() if self.start else None

        end: Union[Unset, None, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat() if self.end else None

        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if current_week is not UNSET:
            field_dict["currentWeek"] = current_week
        if comparison_week is not UNSET:
            field_dict["comparisonWeek"] = comparison_week
        if average_week is not UNSET:
            field_dict["averageWeek"] = average_week
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.week_meta_data_response import WeekMetaDataResponse
        d = src_dict.copy()
        _current_week = d.pop("currentWeek", UNSET)
        current_week: Union[Unset, None, WeekMetaDataResponse]
        if _current_week is None:
            current_week = None
        elif isinstance(_current_week,  Unset):
            current_week = UNSET
        else:
            current_week = WeekMetaDataResponse.from_dict(_current_week)




        _comparison_week = d.pop("comparisonWeek", UNSET)
        comparison_week: Union[Unset, None, WeekMetaDataResponse]
        if _comparison_week is None:
            comparison_week = None
        elif isinstance(_comparison_week,  Unset):
            comparison_week = UNSET
        else:
            comparison_week = WeekMetaDataResponse.from_dict(_comparison_week)




        _average_week = d.pop("averageWeek", UNSET)
        average_week: Union[Unset, None, WeekMetaDataResponse]
        if _average_week is None:
            average_week = None
        elif isinstance(_average_week,  Unset):
            average_week = UNSET
        else:
            average_week = WeekMetaDataResponse.from_dict(_average_week)




        _start = d.pop("start", UNSET)
        start: Union[Unset, None, datetime.date]
        if _start is None:
            start = None
        elif isinstance(_start,  Unset):
            start = UNSET
        else:
            start = isoparse(_start).date()




        _end = d.pop("end", UNSET)
        end: Union[Unset, None, datetime.date]
        if _end is None:
            end = None
        elif isinstance(_end,  Unset):
            end = UNSET
        else:
            end = isoparse(_end).date()




        unit = d.pop("unit", UNSET)

        last_7_days_meta_data_response = cls(
            current_week=current_week,
            comparison_week=comparison_week,
            average_week=average_week,
            start=start,
            end=end,
            unit=unit,
        )

        return last_7_days_meta_data_response

