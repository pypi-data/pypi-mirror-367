from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

import datetime
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import Union
from typing import cast
from typing import Optional






T = TypeVar("T", bound="DayMetaDataResponse")


@attr.s(auto_attribs=True)
class DayMetaDataResponse:
    """ 
        Attributes:
            date (Union[Unset, datetime.date]):
            value (Union[Unset, float]):
            unit (Union[Unset, None, str]):
     """

    date: Union[Unset, datetime.date] = UNSET
    value: Union[Unset, float] = UNSET
    unit: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        value = self.value
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if date is not UNSET:
            field_dict["date"] = date
        if value is not UNSET:
            field_dict["value"] = value
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.date]
        if isinstance(_date,  Unset):
            date = UNSET
        else:
            date = isoparse(_date).date()




        value = d.pop("value", UNSET)

        unit = d.pop("unit", UNSET)

        day_meta_data_response = cls(
            date=date,
            value=value,
            unit=unit,
        )

        return day_meta_data_response

