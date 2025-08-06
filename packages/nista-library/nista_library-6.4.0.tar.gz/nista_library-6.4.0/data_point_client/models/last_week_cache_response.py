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
  from ..models.last_week_meta_data_response import LastWeekMetaDataResponse





T = TypeVar("T", bound="LastWeekCacheResponse")


@attr.s(auto_attribs=True)
class LastWeekCacheResponse:
    """ 
        Attributes:
            last_week_meta_data (Union[Unset, None, List['LastWeekMetaDataResponse']]):
            last_years_weekly_average (Union[Unset, None, float]):
     """

    last_week_meta_data: Union[Unset, None, List['LastWeekMetaDataResponse']] = UNSET
    last_years_weekly_average: Union[Unset, None, float] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.last_week_meta_data_response import LastWeekMetaDataResponse
        last_week_meta_data: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.last_week_meta_data, Unset):
            if self.last_week_meta_data is None:
                last_week_meta_data = None
            else:
                last_week_meta_data = []
                for last_week_meta_data_item_data in self.last_week_meta_data:
                    last_week_meta_data_item = last_week_meta_data_item_data.to_dict()

                    last_week_meta_data.append(last_week_meta_data_item)




        last_years_weekly_average = self.last_years_weekly_average

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if last_week_meta_data is not UNSET:
            field_dict["lastWeekMetaData"] = last_week_meta_data
        if last_years_weekly_average is not UNSET:
            field_dict["lastYearsWeeklyAverage"] = last_years_weekly_average

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.last_week_meta_data_response import LastWeekMetaDataResponse
        d = src_dict.copy()
        last_week_meta_data = []
        _last_week_meta_data = d.pop("lastWeekMetaData", UNSET)
        for last_week_meta_data_item_data in (_last_week_meta_data or []):
            last_week_meta_data_item = LastWeekMetaDataResponse.from_dict(last_week_meta_data_item_data)



            last_week_meta_data.append(last_week_meta_data_item)


        last_years_weekly_average = d.pop("lastYearsWeeklyAverage", UNSET)

        last_week_cache_response = cls(
            last_week_meta_data=last_week_meta_data,
            last_years_weekly_average=last_years_weekly_average,
        )

        return last_week_cache_response

