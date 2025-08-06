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
  from ..models.time_series_quality_response import TimeSeriesQualityResponse





T = TypeVar("T", bound="GetQualityResponse")


@attr.s(auto_attribs=True)
class GetQualityResponse:
    """ 
        Attributes:
            curves (Union[Unset, None, List['TimeSeriesQualityResponse']]):
            time_zone (Union[Unset, None, str]):
     """

    curves: Union[Unset, None, List['TimeSeriesQualityResponse']] = UNSET
    time_zone: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_series_quality_response import TimeSeriesQualityResponse
        curves: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.curves, Unset):
            if self.curves is None:
                curves = None
            else:
                curves = []
                for curves_item_data in self.curves:
                    curves_item = curves_item_data.to_dict()

                    curves.append(curves_item)




        time_zone = self.time_zone

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if curves is not UNSET:
            field_dict["curves"] = curves
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_quality_response import TimeSeriesQualityResponse
        d = src_dict.copy()
        curves = []
        _curves = d.pop("curves", UNSET)
        for curves_item_data in (_curves or []):
            curves_item = TimeSeriesQualityResponse.from_dict(curves_item_data)



            curves.append(curves_item)


        time_zone = d.pop("timeZone", UNSET)

        get_quality_response = cls(
            curves=curves,
            time_zone=time_zone,
        )

        return get_quality_response

