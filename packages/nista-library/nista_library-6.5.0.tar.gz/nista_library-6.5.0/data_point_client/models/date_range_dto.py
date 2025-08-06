from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
import datetime
from typing import Union
from dateutil.parser import isoparse
from ..types import UNSET, Unset






T = TypeVar("T", bound="DateRangeDTO")


@attr.s(auto_attribs=True)
class DateRangeDTO:
    """ 
        Attributes:
            first_entry (Union[Unset, datetime.datetime]):
            last_entry (Union[Unset, datetime.datetime]):
     """

    first_entry: Union[Unset, datetime.datetime] = UNSET
    last_entry: Union[Unset, datetime.datetime] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        first_entry: Union[Unset, str] = UNSET
        if not isinstance(self.first_entry, Unset):
            first_entry = self.first_entry.isoformat()

        last_entry: Union[Unset, str] = UNSET
        if not isinstance(self.last_entry, Unset):
            last_entry = self.last_entry.isoformat()


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if first_entry is not UNSET:
            field_dict["firstEntry"] = first_entry
        if last_entry is not UNSET:
            field_dict["lastEntry"] = last_entry

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _first_entry = d.pop("firstEntry", UNSET)
        first_entry: Union[Unset, datetime.datetime]
        if isinstance(_first_entry,  Unset):
            first_entry = UNSET
        else:
            first_entry = isoparse(_first_entry)




        _last_entry = d.pop("lastEntry", UNSET)
        last_entry: Union[Unset, datetime.datetime]
        if isinstance(_last_entry,  Unset):
            last_entry = UNSET
        else:
            last_entry = isoparse(_last_entry)




        date_range_dto = cls(
            first_entry=first_entry,
            last_entry=last_entry,
        )

        return date_range_dto

