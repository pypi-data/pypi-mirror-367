from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from typing import Union

if TYPE_CHECKING:
  from ..models.day_data_base_transfer import DayDataBaseTransfer





T = TypeVar("T", bound="WeekDataTransfere")


@attr.s(auto_attribs=True)
class WeekDataTransfere:
    """ 
        Attributes:
            discriminator (str):
            monday_data (Union[Unset, None, DayDataBaseTransfer]):
            tuesday_data (Union[Unset, None, DayDataBaseTransfer]):
            wednesday_data (Union[Unset, None, DayDataBaseTransfer]):
            thursday_data (Union[Unset, None, DayDataBaseTransfer]):
            friday_data (Union[Unset, None, DayDataBaseTransfer]):
            saturday_data (Union[Unset, None, DayDataBaseTransfer]):
            sunday_data (Union[Unset, None, DayDataBaseTransfer]):
     """

    discriminator: str
    monday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    tuesday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    wednesday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    thursday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    friday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    saturday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    sunday_data: Union[Unset, None, 'DayDataBaseTransfer'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.day_data_base_transfer import DayDataBaseTransfer
        discriminator = self.discriminator
        monday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.monday_data, Unset):
            monday_data = self.monday_data.to_dict() if self.monday_data else None

        tuesday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.tuesday_data, Unset):
            tuesday_data = self.tuesday_data.to_dict() if self.tuesday_data else None

        wednesday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.wednesday_data, Unset):
            wednesday_data = self.wednesday_data.to_dict() if self.wednesday_data else None

        thursday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.thursday_data, Unset):
            thursday_data = self.thursday_data.to_dict() if self.thursday_data else None

        friday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.friday_data, Unset):
            friday_data = self.friday_data.to_dict() if self.friday_data else None

        saturday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.saturday_data, Unset):
            saturday_data = self.saturday_data.to_dict() if self.saturday_data else None

        sunday_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.sunday_data, Unset):
            sunday_data = self.sunday_data.to_dict() if self.sunday_data else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if monday_data is not UNSET:
            field_dict["mondayData"] = monday_data
        if tuesday_data is not UNSET:
            field_dict["tuesdayData"] = tuesday_data
        if wednesday_data is not UNSET:
            field_dict["wednesdayData"] = wednesday_data
        if thursday_data is not UNSET:
            field_dict["thursdayData"] = thursday_data
        if friday_data is not UNSET:
            field_dict["fridayData"] = friday_data
        if saturday_data is not UNSET:
            field_dict["saturdayData"] = saturday_data
        if sunday_data is not UNSET:
            field_dict["sundayData"] = sunday_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.day_data_base_transfer import DayDataBaseTransfer
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _monday_data = d.pop("mondayData", UNSET)
        monday_data: Union[Unset, None, DayDataBaseTransfer]
        if _monday_data is None:
            monday_data = None
        elif isinstance(_monday_data,  Unset):
            monday_data = UNSET
        else:
            monday_data = DayDataBaseTransfer.from_dict(_monday_data)




        _tuesday_data = d.pop("tuesdayData", UNSET)
        tuesday_data: Union[Unset, None, DayDataBaseTransfer]
        if _tuesday_data is None:
            tuesday_data = None
        elif isinstance(_tuesday_data,  Unset):
            tuesday_data = UNSET
        else:
            tuesday_data = DayDataBaseTransfer.from_dict(_tuesday_data)




        _wednesday_data = d.pop("wednesdayData", UNSET)
        wednesday_data: Union[Unset, None, DayDataBaseTransfer]
        if _wednesday_data is None:
            wednesday_data = None
        elif isinstance(_wednesday_data,  Unset):
            wednesday_data = UNSET
        else:
            wednesday_data = DayDataBaseTransfer.from_dict(_wednesday_data)




        _thursday_data = d.pop("thursdayData", UNSET)
        thursday_data: Union[Unset, None, DayDataBaseTransfer]
        if _thursday_data is None:
            thursday_data = None
        elif isinstance(_thursday_data,  Unset):
            thursday_data = UNSET
        else:
            thursday_data = DayDataBaseTransfer.from_dict(_thursday_data)




        _friday_data = d.pop("fridayData", UNSET)
        friday_data: Union[Unset, None, DayDataBaseTransfer]
        if _friday_data is None:
            friday_data = None
        elif isinstance(_friday_data,  Unset):
            friday_data = UNSET
        else:
            friday_data = DayDataBaseTransfer.from_dict(_friday_data)




        _saturday_data = d.pop("saturdayData", UNSET)
        saturday_data: Union[Unset, None, DayDataBaseTransfer]
        if _saturday_data is None:
            saturday_data = None
        elif isinstance(_saturday_data,  Unset):
            saturday_data = UNSET
        else:
            saturday_data = DayDataBaseTransfer.from_dict(_saturday_data)




        _sunday_data = d.pop("sundayData", UNSET)
        sunday_data: Union[Unset, None, DayDataBaseTransfer]
        if _sunday_data is None:
            sunday_data = None
        elif isinstance(_sunday_data,  Unset):
            sunday_data = UNSET
        else:
            sunday_data = DayDataBaseTransfer.from_dict(_sunday_data)




        week_data_transfere = cls(
            discriminator=discriminator,
            monday_data=monday_data,
            tuesday_data=tuesday_data,
            wednesday_data=wednesday_data,
            thursday_data=thursday_data,
            friday_data=friday_data,
            saturday_data=saturday_data,
            sunday_data=sunday_data,
        )

        week_data_transfere.additional_properties = d
        return week_data_transfere

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
