from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

import datetime
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import Union
from typing import cast
from typing import Optional






T = TypeVar("T", bound="MonthMetaDataResponse")


@attr.s(auto_attribs=True)
class MonthMetaDataResponse:
    """ 
        Attributes:
            month (Union[Unset, int]):
            year (Union[Unset, int]):
            value (Union[Unset, float]):
            start (Union[Unset, None, datetime.date]):
            end (Union[Unset, None, datetime.date]):
     """

    month: Union[Unset, int] = UNSET
    year: Union[Unset, int] = UNSET
    value: Union[Unset, float] = UNSET
    start: Union[Unset, None, datetime.date] = UNSET
    end: Union[Unset, None, datetime.date] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        month = self.month
        year = self.year
        value = self.value
        start: Union[Unset, None, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat() if self.start else None

        end: Union[Unset, None, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat() if self.end else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if month is not UNSET:
            field_dict["month"] = month
        if year is not UNSET:
            field_dict["year"] = year
        if value is not UNSET:
            field_dict["value"] = value
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        month = d.pop("month", UNSET)

        year = d.pop("year", UNSET)

        value = d.pop("value", UNSET)

        _start = d.pop("start", UNSET)
        start: Union[Unset, None, datetime.date]
        if _start is None:
            start = None
        elif isinstance(_start,  Unset):
            start = UNSET
        else:
            start = isoparse(_start).date()




        _end = d.pop("end", UNSET)
        end: Union[Unset, None, datetime.date]
        if _end is None:
            end = None
        elif isinstance(_end,  Unset):
            end = UNSET
        else:
            end = isoparse(_end).date()




        month_meta_data_response = cls(
            month=month,
            year=year,
            value=value,
            start=start,
            end=end,
        )

        return month_meta_data_response

