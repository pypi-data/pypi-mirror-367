from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..models.en_data_point_status import EnDataPointStatus
from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import Optional

if TYPE_CHECKING:
  from ..models.gnista_unit_response import GnistaUnitResponse





T = TypeVar("T", bound="DataPointDataResponse")


@attr.s(auto_attribs=True)
class DataPointDataResponse:
    """ 
        Attributes:
            unit (Union[Unset, None, GnistaUnitResponse]):
            status (Union[Unset, EnDataPointStatus]):
            number_of_data_entries (Union[Unset, int]):
     """

    unit: Union[Unset, None, 'GnistaUnitResponse'] = UNSET
    status: Union[Unset, EnDataPointStatus] = UNSET
    number_of_data_entries: Union[Unset, int] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.gnista_unit_response import GnistaUnitResponse
        unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.unit, Unset):
            unit = self.unit.to_dict() if self.unit else None

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        number_of_data_entries = self.number_of_data_entries

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if unit is not UNSET:
            field_dict["unit"] = unit
        if status is not UNSET:
            field_dict["status"] = status
        if number_of_data_entries is not UNSET:
            field_dict["numberOfDataEntries"] = number_of_data_entries

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gnista_unit_response import GnistaUnitResponse
        d = src_dict.copy()
        _unit = d.pop("unit", UNSET)
        unit: Union[Unset, None, GnistaUnitResponse]
        if _unit is None:
            unit = None
        elif isinstance(_unit,  Unset):
            unit = UNSET
        else:
            unit = GnistaUnitResponse.from_dict(_unit)




        _status = d.pop("status", UNSET)
        status: Union[Unset, EnDataPointStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = EnDataPointStatus(_status)




        number_of_data_entries = d.pop("numberOfDataEntries", UNSET)

        data_point_data_response = cls(
            unit=unit,
            status=status,
            number_of_data_entries=number_of_data_entries,
        )

        return data_point_data_response

