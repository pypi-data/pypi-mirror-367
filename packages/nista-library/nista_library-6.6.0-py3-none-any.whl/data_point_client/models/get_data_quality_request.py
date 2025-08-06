from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import cast, List
from typing import Optional

if TYPE_CHECKING:
  from ..models.time_series_period import TimeSeriesPeriod





T = TypeVar("T", bound="GetDataQualityRequest")


@attr.s(auto_attribs=True)
class GetDataQualityRequest:
    """ 
        Attributes:
            version (Union[Unset, None, int]):
            time_series_periods (Union[Unset, None, List['TimeSeriesPeriod']]):
            remove_time_zone (Union[Unset, bool]):
            time_zone (Union[Unset, None, str]):
     """

    version: Union[Unset, None, int] = UNSET
    time_series_periods: Union[Unset, None, List['TimeSeriesPeriod']] = UNSET
    remove_time_zone: Union[Unset, bool] = UNSET
    time_zone: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_series_period import TimeSeriesPeriod
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




        remove_time_zone = self.remove_time_zone
        time_zone = self.time_zone

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if version is not UNSET:
            field_dict["version"] = version
        if time_series_periods is not UNSET:
            field_dict["timeSeriesPeriods"] = time_series_periods
        if remove_time_zone is not UNSET:
            field_dict["removeTimeZone"] = remove_time_zone
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_period import TimeSeriesPeriod
        d = src_dict.copy()
        version = d.pop("version", UNSET)

        time_series_periods = []
        _time_series_periods = d.pop("timeSeriesPeriods", UNSET)
        for time_series_periods_item_data in (_time_series_periods or []):
            time_series_periods_item = TimeSeriesPeriod.from_dict(time_series_periods_item_data)



            time_series_periods.append(time_series_periods_item)


        remove_time_zone = d.pop("removeTimeZone", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        get_data_quality_request = cls(
            version=version,
            time_series_periods=time_series_periods,
            remove_time_zone=remove_time_zone,
            time_zone=time_zone,
        )

        return get_data_quality_request

