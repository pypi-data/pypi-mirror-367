from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
from typing import cast, List
from typing import Union
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.time_series_period import TimeSeriesPeriod





T = TypeVar("T", bound="GetDataRequest")


@attr.s(auto_attribs=True)
class GetDataRequest:
    """ 
        Attributes:
            window_seconds (Union[Unset, int]):
            version (Union[Unset, None, int]):
            time_series_periods (Union[Unset, None, List['TimeSeriesPeriod']]):
            demanded_unit (Union[Unset, None, str]):
            remove_time_zone (Union[Unset, bool]):
            max_data_point_interpolation_distance_in_seconds (Union[Unset, None, int]):
            time_zone (Union[Unset, None, str]):
     """

    window_seconds: Union[Unset, int] = UNSET
    version: Union[Unset, None, int] = UNSET
    time_series_periods: Union[Unset, None, List['TimeSeriesPeriod']] = UNSET
    demanded_unit: Union[Unset, None, str] = UNSET
    remove_time_zone: Union[Unset, bool] = UNSET
    max_data_point_interpolation_distance_in_seconds: Union[Unset, None, int] = UNSET
    time_zone: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_series_period import TimeSeriesPeriod
        window_seconds = self.window_seconds
        version = self.version
        time_series_periods: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.time_series_periods, Unset):
            if self.time_series_periods is None:
                time_series_periods = None
            else:
                time_series_periods = []
                for time_series_periods_item_data in self.time_series_periods:
                    time_series_periods_item = time_series_periods_item_data.to_dict()

                    time_series_periods.append(time_series_periods_item)




        demanded_unit = self.demanded_unit
        remove_time_zone = self.remove_time_zone
        max_data_point_interpolation_distance_in_seconds = self.max_data_point_interpolation_distance_in_seconds
        time_zone = self.time_zone

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if window_seconds is not UNSET:
            field_dict["windowSeconds"] = window_seconds
        if version is not UNSET:
            field_dict["version"] = version
        if time_series_periods is not UNSET:
            field_dict["timeSeriesPeriods"] = time_series_periods
        if demanded_unit is not UNSET:
            field_dict["demandedUnit"] = demanded_unit
        if remove_time_zone is not UNSET:
            field_dict["removeTimeZone"] = remove_time_zone
        if max_data_point_interpolation_distance_in_seconds is not UNSET:
            field_dict["maxDataPointInterpolationDistanceInSeconds"] = max_data_point_interpolation_distance_in_seconds
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_period import TimeSeriesPeriod
        d = src_dict.copy()
        window_seconds = d.pop("windowSeconds", UNSET)

        version = d.pop("version", UNSET)

        time_series_periods = []
        _time_series_periods = d.pop("timeSeriesPeriods", UNSET)
        for time_series_periods_item_data in (_time_series_periods or []):
            time_series_periods_item = TimeSeriesPeriod.from_dict(time_series_periods_item_data)



            time_series_periods.append(time_series_periods_item)


        demanded_unit = d.pop("demandedUnit", UNSET)

        remove_time_zone = d.pop("removeTimeZone", UNSET)

        max_data_point_interpolation_distance_in_seconds = d.pop("maxDataPointInterpolationDistanceInSeconds", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        get_data_request = cls(
            window_seconds=window_seconds,
            version=version,
            time_series_periods=time_series_periods,
            demanded_unit=demanded_unit,
            remove_time_zone=remove_time_zone,
            max_data_point_interpolation_distance_in_seconds=max_data_point_interpolation_distance_in_seconds,
            time_zone=time_zone,
        )

        return get_data_request

