from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
from typing import Union
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.time_series_quality_response_curve import TimeSeriesQualityResponseCurve





T = TypeVar("T", bound="TimeSeriesQualityResponse")


@attr.s(auto_attribs=True)
class TimeSeriesQualityResponse:
    """ 
        Attributes:
            curve (Union[Unset, None, TimeSeriesQualityResponseCurve]):
     """

    curve: Union[Unset, None, 'TimeSeriesQualityResponseCurve'] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_series_quality_response_curve import TimeSeriesQualityResponseCurve
        curve: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.curve, Unset):
            curve = self.curve.to_dict() if self.curve else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if curve is not UNSET:
            field_dict["curve"] = curve

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_quality_response_curve import TimeSeriesQualityResponseCurve
        d = src_dict.copy()
        _curve = d.pop("curve", UNSET)
        curve: Union[Unset, None, TimeSeriesQualityResponseCurve]
        if _curve is None:
            curve = None
        elif isinstance(_curve,  Unset):
            curve = UNSET
        else:
            curve = TimeSeriesQualityResponseCurve.from_dict(_curve)




        time_series_quality_response = cls(
            curve=curve,
        )

        return time_series_quality_response

