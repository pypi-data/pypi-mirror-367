from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Optional






T = TypeVar("T", bound="ValueOverTimeResponse")


@attr.s(auto_attribs=True)
class ValueOverTimeResponse:
    """ 
        Attributes:
            value (Union[Unset, float]):
            unit (Union[Unset, None, str]):
     """

    value: Union[Unset, float] = UNSET
    unit: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        value = self.value
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if value is not UNSET:
            field_dict["value"] = value
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        value = d.pop("value", UNSET)

        unit = d.pop("unit", UNSET)

        value_over_time_response = cls(
            value=value,
            unit=unit,
        )

        return value_over_time_response

