from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
from typing import Union
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.gnista_unit_response import GnistaUnitResponse
  from ..models.week_data_transfere import WeekDataTransfere





T = TypeVar("T", bound="GetWeekPeriodResponse")


@attr.s(auto_attribs=True)
class GetWeekPeriodResponse:
    """ 
        Attributes:
            discriminator (str):
            week_data (Union[Unset, None, WeekDataTransfere]):
            unit (Union[Unset, None, GnistaUnitResponse]):
     """

    discriminator: str
    week_data: Union[Unset, None, 'WeekDataTransfere'] = UNSET
    unit: Union[Unset, None, 'GnistaUnitResponse'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.week_data_transfere import WeekDataTransfere
        discriminator = self.discriminator
        week_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.week_data, Unset):
            week_data = self.week_data.to_dict() if self.week_data else None

        unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.unit, Unset):
            unit = self.unit.to_dict() if self.unit else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if week_data is not UNSET:
            field_dict["weekData"] = week_data
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.week_data_transfere import WeekDataTransfere
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _week_data = d.pop("weekData", UNSET)
        week_data: Union[Unset, None, WeekDataTransfere]
        if _week_data is None:
            week_data = None
        elif isinstance(_week_data,  Unset):
            week_data = UNSET
        else:
            week_data = WeekDataTransfere.from_dict(_week_data)




        _unit = d.pop("unit", UNSET)
        unit: Union[Unset, None, GnistaUnitResponse]
        if _unit is None:
            unit = None
        elif isinstance(_unit,  Unset):
            unit = UNSET
        else:
            unit = GnistaUnitResponse.from_dict(_unit)




        get_week_period_response = cls(
            discriminator=discriminator,
            week_data=week_data,
            unit=unit,
        )

        get_week_period_response.additional_properties = d
        return get_week_period_response

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
