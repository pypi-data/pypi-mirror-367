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
  from ..models.last_month_meta_data_response import LastMonthMetaDataResponse





T = TypeVar("T", bound="LastMonthCacheResponse")


@attr.s(auto_attribs=True)
class LastMonthCacheResponse:
    """ 
        Attributes:
            last_month_meta_data (Union[Unset, None, List['LastMonthMetaDataResponse']]):
            last_years_monthly_average (Union[Unset, None, float]):
     """

    last_month_meta_data: Union[Unset, None, List['LastMonthMetaDataResponse']] = UNSET
    last_years_monthly_average: Union[Unset, None, float] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.last_month_meta_data_response import LastMonthMetaDataResponse
        last_month_meta_data: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.last_month_meta_data, Unset):
            if self.last_month_meta_data is None:
                last_month_meta_data = None
            else:
                last_month_meta_data = []
                for last_month_meta_data_item_data in self.last_month_meta_data:
                    last_month_meta_data_item = last_month_meta_data_item_data.to_dict()

                    last_month_meta_data.append(last_month_meta_data_item)




        last_years_monthly_average = self.last_years_monthly_average

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if last_month_meta_data is not UNSET:
            field_dict["lastMonthMetaData"] = last_month_meta_data
        if last_years_monthly_average is not UNSET:
            field_dict["lastYearsMonthlyAverage"] = last_years_monthly_average

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.last_month_meta_data_response import LastMonthMetaDataResponse
        d = src_dict.copy()
        last_month_meta_data = []
        _last_month_meta_data = d.pop("lastMonthMetaData", UNSET)
        for last_month_meta_data_item_data in (_last_month_meta_data or []):
            last_month_meta_data_item = LastMonthMetaDataResponse.from_dict(last_month_meta_data_item_data)



            last_month_meta_data.append(last_month_meta_data_item)


        last_years_monthly_average = d.pop("lastYearsMonthlyAverage", UNSET)

        last_month_cache_response = cls(
            last_month_meta_data=last_month_meta_data,
            last_years_monthly_average=last_years_monthly_average,
        )

        return last_month_cache_response

