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
  from ..models.quarterly_comparison_response import QuarterlyComparisonResponse





T = TypeVar("T", bound="QuarterlyComparisonCacheResponse")


@attr.s(auto_attribs=True)
class QuarterlyComparisonCacheResponse:
    """ 
        Attributes:
            quarterly_comparison_meta_data (Union[Unset, None, List['QuarterlyComparisonResponse']]):
            last_years_quarterly_average (Union[Unset, None, float]):
     """

    quarterly_comparison_meta_data: Union[Unset, None, List['QuarterlyComparisonResponse']] = UNSET
    last_years_quarterly_average: Union[Unset, None, float] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.quarterly_comparison_response import QuarterlyComparisonResponse
        quarterly_comparison_meta_data: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.quarterly_comparison_meta_data, Unset):
            if self.quarterly_comparison_meta_data is None:
                quarterly_comparison_meta_data = None
            else:
                quarterly_comparison_meta_data = []
                for quarterly_comparison_meta_data_item_data in self.quarterly_comparison_meta_data:
                    quarterly_comparison_meta_data_item = quarterly_comparison_meta_data_item_data.to_dict()

                    quarterly_comparison_meta_data.append(quarterly_comparison_meta_data_item)




        last_years_quarterly_average = self.last_years_quarterly_average

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if quarterly_comparison_meta_data is not UNSET:
            field_dict["quarterlyComparisonMetaData"] = quarterly_comparison_meta_data
        if last_years_quarterly_average is not UNSET:
            field_dict["lastYearsQuarterlyAverage"] = last_years_quarterly_average

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.quarterly_comparison_response import QuarterlyComparisonResponse
        d = src_dict.copy()
        quarterly_comparison_meta_data = []
        _quarterly_comparison_meta_data = d.pop("quarterlyComparisonMetaData", UNSET)
        for quarterly_comparison_meta_data_item_data in (_quarterly_comparison_meta_data or []):
            quarterly_comparison_meta_data_item = QuarterlyComparisonResponse.from_dict(quarterly_comparison_meta_data_item_data)



            quarterly_comparison_meta_data.append(quarterly_comparison_meta_data_item)


        last_years_quarterly_average = d.pop("lastYearsQuarterlyAverage", UNSET)

        quarterly_comparison_cache_response = cls(
            quarterly_comparison_meta_data=quarterly_comparison_meta_data,
            last_years_quarterly_average=last_years_quarterly_average,
        )

        return quarterly_comparison_cache_response

