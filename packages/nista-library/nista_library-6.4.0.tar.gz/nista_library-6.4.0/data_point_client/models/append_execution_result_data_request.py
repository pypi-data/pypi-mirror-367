from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import cast

if TYPE_CHECKING:
  from ..models.sub_series_request import SubSeriesRequest





T = TypeVar("T", bound="AppendExecutionResultDataRequest")


@attr.s(auto_attribs=True)
class AppendExecutionResultDataRequest:
    """ 
        Attributes:
            sub_series (List['SubSeriesRequest']):
     """

    sub_series: List['SubSeriesRequest']


    def to_dict(self) -> Dict[str, Any]:
        from ..models.sub_series_request import SubSeriesRequest
        sub_series = []
        for sub_series_item_data in self.sub_series:
            sub_series_item = sub_series_item_data.to_dict()

            sub_series.append(sub_series_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "subSeries": sub_series,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sub_series_request import SubSeriesRequest
        d = src_dict.copy()
        sub_series = []
        _sub_series = d.pop("subSeries")
        for sub_series_item_data in (_sub_series):
            sub_series_item = SubSeriesRequest.from_dict(sub_series_item_data)



            sub_series.append(sub_series_item)


        append_execution_result_data_request = cls(
            sub_series=sub_series,
        )

        return append_execution_result_data_request

