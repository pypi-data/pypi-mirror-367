from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..models.en_data_point_value_type_dto import EnDataPointValueTypeDTO
from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import cast, List
from typing import Optional

if TYPE_CHECKING:
  from ..models.date_range_dto import DateRangeDTO





T = TypeVar("T", bound="FinishExecutionResultDataRequest")


@attr.s(auto_attribs=True)
class FinishExecutionResultDataRequest:
    """ 
        Attributes:
            unit (Union[Unset, None, str]):
            time_zone (Union[Unset, None, str]):
            is_major_change (Union[Unset, bool]):
            sub_series (Union[Unset, None, List['DateRangeDTO']]):
            data_interval_in_seconds (Union[Unset, int]):
            data_point_value_type (Union[Unset, None, EnDataPointValueTypeDTO]):
     """

    unit: Union[Unset, None, str] = UNSET
    time_zone: Union[Unset, None, str] = UNSET
    is_major_change: Union[Unset, bool] = UNSET
    sub_series: Union[Unset, None, List['DateRangeDTO']] = UNSET
    data_interval_in_seconds: Union[Unset, int] = UNSET
    data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.date_range_dto import DateRangeDTO
        unit = self.unit
        time_zone = self.time_zone
        is_major_change = self.is_major_change
        sub_series: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sub_series, Unset):
            if self.sub_series is None:
                sub_series = None
            else:
                sub_series = []
                for sub_series_item_data in self.sub_series:
                    sub_series_item = sub_series_item_data.to_dict()

                    sub_series.append(sub_series_item)




        data_interval_in_seconds = self.data_interval_in_seconds
        data_point_value_type: Union[Unset, None, str] = UNSET
        if not isinstance(self.data_point_value_type, Unset):
            data_point_value_type = self.data_point_value_type.value if self.data_point_value_type else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if unit is not UNSET:
            field_dict["unit"] = unit
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if is_major_change is not UNSET:
            field_dict["isMajorChange"] = is_major_change
        if sub_series is not UNSET:
            field_dict["subSeries"] = sub_series
        if data_interval_in_seconds is not UNSET:
            field_dict["dataIntervalInSeconds"] = data_interval_in_seconds
        if data_point_value_type is not UNSET:
            field_dict["dataPointValueType"] = data_point_value_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.date_range_dto import DateRangeDTO
        d = src_dict.copy()
        unit = d.pop("unit", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        is_major_change = d.pop("isMajorChange", UNSET)

        sub_series = []
        _sub_series = d.pop("subSeries", UNSET)
        for sub_series_item_data in (_sub_series or []):
            sub_series_item = DateRangeDTO.from_dict(sub_series_item_data)



            sub_series.append(sub_series_item)


        data_interval_in_seconds = d.pop("dataIntervalInSeconds", UNSET)

        _data_point_value_type = d.pop("dataPointValueType", UNSET)
        data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO]
        if _data_point_value_type is None:
            data_point_value_type = None
        elif isinstance(_data_point_value_type,  Unset):
            data_point_value_type = UNSET
        else:
            data_point_value_type = EnDataPointValueTypeDTO(_data_point_value_type)




        finish_execution_result_data_request = cls(
            unit=unit,
            time_zone=time_zone,
            is_major_change=is_major_change,
            sub_series=sub_series,
            data_interval_in_seconds=data_interval_in_seconds,
            data_point_value_type=data_point_value_type,
        )

        return finish_execution_result_data_request

