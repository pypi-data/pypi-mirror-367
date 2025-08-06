from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from dateutil.parser import isoparse
import datetime
from typing import Union






T = TypeVar("T", bound="DayDataByHourTransfer")


@attr.s(auto_attribs=True)
class DayDataByHourTransfer:
    """ 
        Attributes:
            discriminator (str):
            date (Union[Unset, None, datetime.datetime]):
            h0 (Union[Unset, None, float]):
            h1 (Union[Unset, None, float]):
            h2 (Union[Unset, None, float]):
            h3 (Union[Unset, None, float]):
            h4 (Union[Unset, None, float]):
            h5 (Union[Unset, None, float]):
            h6 (Union[Unset, None, float]):
            h7 (Union[Unset, None, float]):
            h8 (Union[Unset, None, float]):
            h9 (Union[Unset, None, float]):
            h10 (Union[Unset, None, float]):
            h11 (Union[Unset, None, float]):
            h12 (Union[Unset, None, float]):
            h13 (Union[Unset, None, float]):
            h14 (Union[Unset, None, float]):
            h15 (Union[Unset, None, float]):
            h16 (Union[Unset, None, float]):
            h17 (Union[Unset, None, float]):
            h18 (Union[Unset, None, float]):
            h19 (Union[Unset, None, float]):
            h20 (Union[Unset, None, float]):
            h21 (Union[Unset, None, float]):
            h22 (Union[Unset, None, float]):
            h23 (Union[Unset, None, float]):
     """

    discriminator: str
    date: Union[Unset, None, datetime.datetime] = UNSET
    h0: Union[Unset, None, float] = UNSET
    h1: Union[Unset, None, float] = UNSET
    h2: Union[Unset, None, float] = UNSET
    h3: Union[Unset, None, float] = UNSET
    h4: Union[Unset, None, float] = UNSET
    h5: Union[Unset, None, float] = UNSET
    h6: Union[Unset, None, float] = UNSET
    h7: Union[Unset, None, float] = UNSET
    h8: Union[Unset, None, float] = UNSET
    h9: Union[Unset, None, float] = UNSET
    h10: Union[Unset, None, float] = UNSET
    h11: Union[Unset, None, float] = UNSET
    h12: Union[Unset, None, float] = UNSET
    h13: Union[Unset, None, float] = UNSET
    h14: Union[Unset, None, float] = UNSET
    h15: Union[Unset, None, float] = UNSET
    h16: Union[Unset, None, float] = UNSET
    h17: Union[Unset, None, float] = UNSET
    h18: Union[Unset, None, float] = UNSET
    h19: Union[Unset, None, float] = UNSET
    h20: Union[Unset, None, float] = UNSET
    h21: Union[Unset, None, float] = UNSET
    h22: Union[Unset, None, float] = UNSET
    h23: Union[Unset, None, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        date: Union[Unset, None, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat() if self.date else None

        h0 = self.h0
        h1 = self.h1
        h2 = self.h2
        h3 = self.h3
        h4 = self.h4
        h5 = self.h5
        h6 = self.h6
        h7 = self.h7
        h8 = self.h8
        h9 = self.h9
        h10 = self.h10
        h11 = self.h11
        h12 = self.h12
        h13 = self.h13
        h14 = self.h14
        h15 = self.h15
        h16 = self.h16
        h17 = self.h17
        h18 = self.h18
        h19 = self.h19
        h20 = self.h20
        h21 = self.h21
        h22 = self.h22
        h23 = self.h23

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if date is not UNSET:
            field_dict["date"] = date
        if h0 is not UNSET:
            field_dict["h0"] = h0
        if h1 is not UNSET:
            field_dict["h1"] = h1
        if h2 is not UNSET:
            field_dict["h2"] = h2
        if h3 is not UNSET:
            field_dict["h3"] = h3
        if h4 is not UNSET:
            field_dict["h4"] = h4
        if h5 is not UNSET:
            field_dict["h5"] = h5
        if h6 is not UNSET:
            field_dict["h6"] = h6
        if h7 is not UNSET:
            field_dict["h7"] = h7
        if h8 is not UNSET:
            field_dict["h8"] = h8
        if h9 is not UNSET:
            field_dict["h9"] = h9
        if h10 is not UNSET:
            field_dict["h10"] = h10
        if h11 is not UNSET:
            field_dict["h11"] = h11
        if h12 is not UNSET:
            field_dict["h12"] = h12
        if h13 is not UNSET:
            field_dict["h13"] = h13
        if h14 is not UNSET:
            field_dict["h14"] = h14
        if h15 is not UNSET:
            field_dict["h15"] = h15
        if h16 is not UNSET:
            field_dict["h16"] = h16
        if h17 is not UNSET:
            field_dict["h17"] = h17
        if h18 is not UNSET:
            field_dict["h18"] = h18
        if h19 is not UNSET:
            field_dict["h19"] = h19
        if h20 is not UNSET:
            field_dict["h20"] = h20
        if h21 is not UNSET:
            field_dict["h21"] = h21
        if h22 is not UNSET:
            field_dict["h22"] = h22
        if h23 is not UNSET:
            field_dict["h23"] = h23

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _date = d.pop("date", UNSET)
        date: Union[Unset, None, datetime.datetime]
        if _date is None:
            date = None
        elif isinstance(_date,  Unset):
            date = UNSET
        else:
            date = isoparse(_date)




        h0 = d.pop("h0", UNSET)

        h1 = d.pop("h1", UNSET)

        h2 = d.pop("h2", UNSET)

        h3 = d.pop("h3", UNSET)

        h4 = d.pop("h4", UNSET)

        h5 = d.pop("h5", UNSET)

        h6 = d.pop("h6", UNSET)

        h7 = d.pop("h7", UNSET)

        h8 = d.pop("h8", UNSET)

        h9 = d.pop("h9", UNSET)

        h10 = d.pop("h10", UNSET)

        h11 = d.pop("h11", UNSET)

        h12 = d.pop("h12", UNSET)

        h13 = d.pop("h13", UNSET)

        h14 = d.pop("h14", UNSET)

        h15 = d.pop("h15", UNSET)

        h16 = d.pop("h16", UNSET)

        h17 = d.pop("h17", UNSET)

        h18 = d.pop("h18", UNSET)

        h19 = d.pop("h19", UNSET)

        h20 = d.pop("h20", UNSET)

        h21 = d.pop("h21", UNSET)

        h22 = d.pop("h22", UNSET)

        h23 = d.pop("h23", UNSET)

        day_data_by_hour_transfer = cls(
            discriminator=discriminator,
            date=date,
            h0=h0,
            h1=h1,
            h2=h2,
            h3=h3,
            h4=h4,
            h5=h5,
            h6=h6,
            h7=h7,
            h8=h8,
            h9=h9,
            h10=h10,
            h11=h11,
            h12=h12,
            h13=h13,
            h14=h14,
            h15=h15,
            h16=h16,
            h17=h17,
            h18=h18,
            h19=h19,
            h20=h20,
            h21=h21,
            h22=h22,
            h23=h23,
        )

        day_data_by_hour_transfer.additional_properties = d
        return day_data_by_hour_transfer

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
