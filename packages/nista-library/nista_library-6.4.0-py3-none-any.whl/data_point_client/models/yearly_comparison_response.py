from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from dateutil.parser import isoparse
import datetime
from typing import Union

if TYPE_CHECKING:
  from ..models.month_meta_data_response import MonthMetaDataResponse





T = TypeVar("T", bound="YearlyComparisonResponse")


@attr.s(auto_attribs=True)
class YearlyComparisonResponse:
    """ 
        Attributes:
            current_months (Union[Unset, None, List['MonthMetaDataResponse']]):
            comparison_months (Union[Unset, None, List['MonthMetaDataResponse']]):
            current_year_value (Union[Unset, None, float]):
            comparison_year_value (Union[Unset, None, float]):
            average_month (Union[Unset, None, float]):
            unit (Union[Unset, None, str]):
            start (Union[Unset, None, datetime.date]):
            end (Union[Unset, None, datetime.date]):
            last_years_total_consumption (Union[Unset, None, float]):
     """

    current_months: Union[Unset, None, List['MonthMetaDataResponse']] = UNSET
    comparison_months: Union[Unset, None, List['MonthMetaDataResponse']] = UNSET
    current_year_value: Union[Unset, None, float] = UNSET
    comparison_year_value: Union[Unset, None, float] = UNSET
    average_month: Union[Unset, None, float] = UNSET
    unit: Union[Unset, None, str] = UNSET
    start: Union[Unset, None, datetime.date] = UNSET
    end: Union[Unset, None, datetime.date] = UNSET
    last_years_total_consumption: Union[Unset, None, float] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.month_meta_data_response import MonthMetaDataResponse
        current_months: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.current_months, Unset):
            if self.current_months is None:
                current_months = None
            else:
                current_months = []
                for current_months_item_data in self.current_months:
                    current_months_item = current_months_item_data.to_dict()

                    current_months.append(current_months_item)




        comparison_months: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.comparison_months, Unset):
            if self.comparison_months is None:
                comparison_months = None
            else:
                comparison_months = []
                for comparison_months_item_data in self.comparison_months:
                    comparison_months_item = comparison_months_item_data.to_dict()

                    comparison_months.append(comparison_months_item)




        current_year_value = self.current_year_value
        comparison_year_value = self.comparison_year_value
        average_month = self.average_month
        unit = self.unit
        start: Union[Unset, None, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat() if self.start else None

        end: Union[Unset, None, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat() if self.end else None

        last_years_total_consumption = self.last_years_total_consumption

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if current_months is not UNSET:
            field_dict["currentMonths"] = current_months
        if comparison_months is not UNSET:
            field_dict["comparisonMonths"] = comparison_months
        if current_year_value is not UNSET:
            field_dict["currentYearValue"] = current_year_value
        if comparison_year_value is not UNSET:
            field_dict["comparisonYearValue"] = comparison_year_value
        if average_month is not UNSET:
            field_dict["averageMonth"] = average_month
        if unit is not UNSET:
            field_dict["unit"] = unit
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if last_years_total_consumption is not UNSET:
            field_dict["lastYearsTotalConsumption"] = last_years_total_consumption

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.month_meta_data_response import MonthMetaDataResponse
        d = src_dict.copy()
        current_months = []
        _current_months = d.pop("currentMonths", UNSET)
        for current_months_item_data in (_current_months or []):
            current_months_item = MonthMetaDataResponse.from_dict(current_months_item_data)



            current_months.append(current_months_item)


        comparison_months = []
        _comparison_months = d.pop("comparisonMonths", UNSET)
        for comparison_months_item_data in (_comparison_months or []):
            comparison_months_item = MonthMetaDataResponse.from_dict(comparison_months_item_data)



            comparison_months.append(comparison_months_item)


        current_year_value = d.pop("currentYearValue", UNSET)

        comparison_year_value = d.pop("comparisonYearValue", UNSET)

        average_month = d.pop("averageMonth", UNSET)

        unit = d.pop("unit", UNSET)

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




        last_years_total_consumption = d.pop("lastYearsTotalConsumption", UNSET)

        yearly_comparison_response = cls(
            current_months=current_months,
            comparison_months=comparison_months,
            current_year_value=current_year_value,
            comparison_year_value=comparison_year_value,
            average_month=average_month,
            unit=unit,
            start=start,
            end=end,
            last_years_total_consumption=last_years_total_consumption,
        )

        return yearly_comparison_response

