from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Optional






T = TypeVar("T", bound="DataPointDataBase")


@attr.s(auto_attribs=True)
class DataPointDataBase:
    """ 
        Attributes:
            discriminator (str):
            status (Union[Unset, None, str]):
            error_message (Union[Unset, None, str]):
            unit (Union[Unset, None, str]):
            number_of_entries (Union[Unset, int]):
     """

    discriminator: str
    status: Union[Unset, None, str] = UNSET
    error_message: Union[Unset, None, str] = UNSET
    unit: Union[Unset, None, str] = UNSET
    number_of_entries: Union[Unset, int] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        status = self.status
        error_message = self.error_message
        unit = self.unit
        number_of_entries = self.number_of_entries

        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "discriminator": discriminator,
        })
        if status is not UNSET:
            field_dict["status"] = status
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if unit is not UNSET:
            field_dict["unit"] = unit
        if number_of_entries is not UNSET:
            field_dict["numberOfEntries"] = number_of_entries

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        status = d.pop("status", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        unit = d.pop("unit", UNSET)

        number_of_entries = d.pop("numberOfEntries", UNSET)

        data_point_data_base = cls(
            discriminator=discriminator,
            status=status,
            error_message=error_message,
            unit=unit,
            number_of_entries=number_of_entries,
        )

        return data_point_data_base

