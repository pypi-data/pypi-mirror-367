from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
import datetime
from typing import cast, List
from typing import Union
from dateutil.parser import isoparse
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.day_meta_data_response import DayMetaDataResponse





T = TypeVar("T", bound="WeekMetaDataResponse")


@attr.s(auto_attribs=True)
class WeekMetaDataResponse:
    """ 
        Attributes:
            days (Union[Unset, None, List['DayMetaDataResponse']]):
            value (Union[Unset, None, float]):
            start_date (Union[Unset, None, datetime.date]):
            end_date (Union[Unset, None, datetime.date]):
            expected_start_date (Union[Unset, None, datetime.date]):
            expected_end_date (Union[Unset, None, datetime.date]):
     """

    days: Union[Unset, None, List['DayMetaDataResponse']] = UNSET
    value: Union[Unset, None, float] = UNSET
    start_date: Union[Unset, None, datetime.date] = UNSET
    end_date: Union[Unset, None, datetime.date] = UNSET
    expected_start_date: Union[Unset, None, datetime.date] = UNSET
    expected_end_date: Union[Unset, None, datetime.date] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.day_meta_data_response import DayMetaDataResponse
        days: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.days, Unset):
            if self.days is None:
                days = None
            else:
                days = []
                for days_item_data in self.days:
                    days_item = days_item_data.to_dict()

                    days.append(days_item)




        value = self.value
        start_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat() if self.start_date else None

        end_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat() if self.end_date else None

        expected_start_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.expected_start_date, Unset):
            expected_start_date = self.expected_start_date.isoformat() if self.expected_start_date else None

        expected_end_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.expected_end_date, Unset):
            expected_end_date = self.expected_end_date.isoformat() if self.expected_end_date else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if days is not UNSET:
            field_dict["days"] = days
        if value is not UNSET:
            field_dict["value"] = value
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if expected_start_date is not UNSET:
            field_dict["expectedStartDate"] = expected_start_date
        if expected_end_date is not UNSET:
            field_dict["expectedEndDate"] = expected_end_date

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.day_meta_data_response import DayMetaDataResponse
        d = src_dict.copy()
        days = []
        _days = d.pop("days", UNSET)
        for days_item_data in (_days or []):
            days_item = DayMetaDataResponse.from_dict(days_item_data)



            days.append(days_item)


        value = d.pop("value", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, None, datetime.date]
        if _start_date is None:
            start_date = None
        elif isinstance(_start_date,  Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date).date()




        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, None, datetime.date]
        if _end_date is None:
            end_date = None
        elif isinstance(_end_date,  Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date).date()




        _expected_start_date = d.pop("expectedStartDate", UNSET)
        expected_start_date: Union[Unset, None, datetime.date]
        if _expected_start_date is None:
            expected_start_date = None
        elif isinstance(_expected_start_date,  Unset):
            expected_start_date = UNSET
        else:
            expected_start_date = isoparse(_expected_start_date).date()




        _expected_end_date = d.pop("expectedEndDate", UNSET)
        expected_end_date: Union[Unset, None, datetime.date]
        if _expected_end_date is None:
            expected_end_date = None
        elif isinstance(_expected_end_date,  Unset):
            expected_end_date = UNSET
        else:
            expected_end_date = isoparse(_expected_end_date).date()




        week_meta_data_response = cls(
            days=days,
            value=value,
            start_date=start_date,
            end_date=end_date,
            expected_start_date=expected_start_date,
            expected_end_date=expected_end_date,
        )

        return week_meta_data_response

