from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from typing import Union

if TYPE_CHECKING:
  from ..models.week_meta_data_response import WeekMetaDataResponse





T = TypeVar("T", bound="LastMonthMetaDataResponse")


@attr.s(auto_attribs=True)
class LastMonthMetaDataResponse:
    """ 
        Attributes:
            current_month (Union[Unset, None, List['WeekMetaDataResponse']]):
            comparison_month (Union[Unset, None, List['WeekMetaDataResponse']]):
            current_month_value (Union[Unset, None, float]):
            comparison_month_value (Union[Unset, None, float]):
            average_week (Union[Unset, None, float]):
            unit (Union[Unset, None, str]):
     """

    current_month: Union[Unset, None, List['WeekMetaDataResponse']] = UNSET
    comparison_month: Union[Unset, None, List['WeekMetaDataResponse']] = UNSET
    current_month_value: Union[Unset, None, float] = UNSET
    comparison_month_value: Union[Unset, None, float] = UNSET
    average_week: Union[Unset, None, float] = UNSET
    unit: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.week_meta_data_response import WeekMetaDataResponse
        current_month: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.current_month, Unset):
            if self.current_month is None:
                current_month = None
            else:
                current_month = []
                for current_month_item_data in self.current_month:
                    current_month_item = current_month_item_data.to_dict()

                    current_month.append(current_month_item)




        comparison_month: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.comparison_month, Unset):
            if self.comparison_month is None:
                comparison_month = None
            else:
                comparison_month = []
                for comparison_month_item_data in self.comparison_month:
                    comparison_month_item = comparison_month_item_data.to_dict()

                    comparison_month.append(comparison_month_item)




        current_month_value = self.current_month_value
        comparison_month_value = self.comparison_month_value
        average_week = self.average_week
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if current_month is not UNSET:
            field_dict["currentMonth"] = current_month
        if comparison_month is not UNSET:
            field_dict["comparisonMonth"] = comparison_month
        if current_month_value is not UNSET:
            field_dict["currentMonthValue"] = current_month_value
        if comparison_month_value is not UNSET:
            field_dict["comparisonMonthValue"] = comparison_month_value
        if average_week is not UNSET:
            field_dict["averageWeek"] = average_week
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.week_meta_data_response import WeekMetaDataResponse
        d = src_dict.copy()
        current_month = []
        _current_month = d.pop("currentMonth", UNSET)
        for current_month_item_data in (_current_month or []):
            current_month_item = WeekMetaDataResponse.from_dict(current_month_item_data)



            current_month.append(current_month_item)


        comparison_month = []
        _comparison_month = d.pop("comparisonMonth", UNSET)
        for comparison_month_item_data in (_comparison_month or []):
            comparison_month_item = WeekMetaDataResponse.from_dict(comparison_month_item_data)



            comparison_month.append(comparison_month_item)


        current_month_value = d.pop("currentMonthValue", UNSET)

        comparison_month_value = d.pop("comparisonMonthValue", UNSET)

        average_week = d.pop("averageWeek", UNSET)

        unit = d.pop("unit", UNSET)

        last_month_meta_data_response = cls(
            current_month=current_month,
            comparison_month=comparison_month,
            current_month_value=current_month_value,
            comparison_month_value=comparison_month_value,
            average_week=average_week,
            unit=unit,
        )

        return last_month_meta_data_response

