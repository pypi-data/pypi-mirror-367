from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from dateutil.parser import isoparse
import datetime
from typing import Union

if TYPE_CHECKING:
  from ..models.time_series_response_curve import TimeSeriesResponseCurve





T = TypeVar("T", bound="TimeSeriesResponse")


@attr.s(auto_attribs=True)
class TimeSeriesResponse:
    """ 
        Attributes:
            discriminator (str):
            range_start (Union[Unset, datetime.datetime]):
            range_end (Union[Unset, datetime.datetime]):
            curve (Union[Unset, None, TimeSeriesResponseCurve]):
     """

    discriminator: str
    range_start: Union[Unset, datetime.datetime] = UNSET
    range_end: Union[Unset, datetime.datetime] = UNSET
    curve: Union[Unset, None, 'TimeSeriesResponseCurve'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_series_response_curve import TimeSeriesResponseCurve
        discriminator = self.discriminator
        range_start: Union[Unset, str] = UNSET
        if not isinstance(self.range_start, Unset):
            range_start = self.range_start.isoformat()

        range_end: Union[Unset, str] = UNSET
        if not isinstance(self.range_end, Unset):
            range_end = self.range_end.isoformat()

        curve: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.curve, Unset):
            curve = self.curve.to_dict() if self.curve else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if range_start is not UNSET:
            field_dict["rangeStart"] = range_start
        if range_end is not UNSET:
            field_dict["rangeEnd"] = range_end
        if curve is not UNSET:
            field_dict["curve"] = curve

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_response_curve import TimeSeriesResponseCurve
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _range_start = d.pop("rangeStart", UNSET)
        range_start: Union[Unset, datetime.datetime]
        if isinstance(_range_start,  Unset):
            range_start = UNSET
        else:
            range_start = isoparse(_range_start)




        _range_end = d.pop("rangeEnd", UNSET)
        range_end: Union[Unset, datetime.datetime]
        if isinstance(_range_end,  Unset):
            range_end = UNSET
        else:
            range_end = isoparse(_range_end)




        _curve = d.pop("curve", UNSET)
        curve: Union[Unset, None, TimeSeriesResponseCurve]
        if _curve is None:
            curve = None
        elif isinstance(_curve,  Unset):
            curve = UNSET
        else:
            curve = TimeSeriesResponseCurve.from_dict(_curve)




        time_series_response = cls(
            discriminator=discriminator,
            range_start=range_start,
            range_end=range_end,
            curve=curve,
        )

        time_series_response.additional_properties = d
        return time_series_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
