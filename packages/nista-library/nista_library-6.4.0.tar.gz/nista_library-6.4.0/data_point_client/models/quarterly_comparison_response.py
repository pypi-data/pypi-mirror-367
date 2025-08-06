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





T = TypeVar("T", bound="QuarterlyComparisonResponse")


@attr.s(auto_attribs=True)
class QuarterlyComparisonResponse:
    """ 
        Attributes:
            current_months (Union[Unset, None, List['MonthMetaDataResponse']]):
            comparison_months (Union[Unset, None, List['MonthMetaDataResponse']]):
            current_quarter_value (Union[Unset, None, float]):
            comparison_quarter_value (Union[Unset, None, float]):
            current_start (Union[Unset, None, datetime.date]):
            current_end (Union[Unset, None, datetime.date]):
            comparison_start (Union[Unset, None, datetime.date]):
            comparison_end (Union[Unset, None, datetime.date]):
            average_month (Union[Unset, None, float]):
            unit (Union[Unset, None, str]):
     """

    current_months: Union[Unset, None, List['MonthMetaDataResponse']] = UNSET
    comparison_months: Union[Unset, None, List['MonthMetaDataResponse']] = UNSET
    current_quarter_value: Union[Unset, None, float] = UNSET
    comparison_quarter_value: Union[Unset, None, float] = UNSET
    current_start: Union[Unset, None, datetime.date] = UNSET
    current_end: Union[Unset, None, datetime.date] = UNSET
    comparison_start: Union[Unset, None, datetime.date] = UNSET
    comparison_end: Union[Unset, None, datetime.date] = UNSET
    average_month: Union[Unset, None, float] = UNSET
    unit: Union[Unset, None, str] = UNSET


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




        current_quarter_value = self.current_quarter_value
        comparison_quarter_value = self.comparison_quarter_value
        current_start: Union[Unset, None, str] = UNSET
        if not isinstance(self.current_start, Unset):
            current_start = self.current_start.isoformat() if self.current_start else None

        current_end: Union[Unset, None, str] = UNSET
        if not isinstance(self.current_end, Unset):
            current_end = self.current_end.isoformat() if self.current_end else None

        comparison_start: Union[Unset, None, str] = UNSET
        if not isinstance(self.comparison_start, Unset):
            comparison_start = self.comparison_start.isoformat() if self.comparison_start else None

        comparison_end: Union[Unset, None, str] = UNSET
        if not isinstance(self.comparison_end, Unset):
            comparison_end = self.comparison_end.isoformat() if self.comparison_end else None

        average_month = self.average_month
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if current_months is not UNSET:
            field_dict["currentMonths"] = current_months
        if comparison_months is not UNSET:
            field_dict["comparisonMonths"] = comparison_months
        if current_quarter_value is not UNSET:
            field_dict["currentQuarterValue"] = current_quarter_value
        if comparison_quarter_value is not UNSET:
            field_dict["comparisonQuarterValue"] = comparison_quarter_value
        if current_start is not UNSET:
            field_dict["currentStart"] = current_start
        if current_end is not UNSET:
            field_dict["currentEnd"] = current_end
        if comparison_start is not UNSET:
            field_dict["comparisonStart"] = comparison_start
        if comparison_end is not UNSET:
            field_dict["comparisonEnd"] = comparison_end
        if average_month is not UNSET:
            field_dict["averageMonth"] = average_month
        if unit is not UNSET:
            field_dict["unit"] = unit

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


        current_quarter_value = d.pop("currentQuarterValue", UNSET)

        comparison_quarter_value = d.pop("comparisonQuarterValue", UNSET)

        _current_start = d.pop("currentStart", UNSET)
        current_start: Union[Unset, None, datetime.date]
        if _current_start is None:
            current_start = None
        elif isinstance(_current_start,  Unset):
            current_start = UNSET
        else:
            current_start = isoparse(_current_start).date()




        _current_end = d.pop("currentEnd", UNSET)
        current_end: Union[Unset, None, datetime.date]
        if _current_end is None:
            current_end = None
        elif isinstance(_current_end,  Unset):
            current_end = UNSET
        else:
            current_end = isoparse(_current_end).date()




        _comparison_start = d.pop("comparisonStart", UNSET)
        comparison_start: Union[Unset, None, datetime.date]
        if _comparison_start is None:
            comparison_start = None
        elif isinstance(_comparison_start,  Unset):
            comparison_start = UNSET
        else:
            comparison_start = isoparse(_comparison_start).date()




        _comparison_end = d.pop("comparisonEnd", UNSET)
        comparison_end: Union[Unset, None, datetime.date]
        if _comparison_end is None:
            comparison_end = None
        elif isinstance(_comparison_end,  Unset):
            comparison_end = UNSET
        else:
            comparison_end = isoparse(_comparison_end).date()




        average_month = d.pop("averageMonth", UNSET)

        unit = d.pop("unit", UNSET)

        quarterly_comparison_response = cls(
            current_months=current_months,
            comparison_months=comparison_months,
            current_quarter_value=current_quarter_value,
            comparison_quarter_value=comparison_quarter_value,
            current_start=current_start,
            current_end=current_end,
            comparison_start=comparison_start,
            comparison_end=comparison_end,
            average_month=average_month,
            unit=unit,
        )

        return quarterly_comparison_response

