from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Optional






T = TypeVar("T", bound="DataExportRequest")


@attr.s(auto_attribs=True)
class DataExportRequest:
    """ 
        Attributes:
            data_point_id (str):
            separator (str):
            version (int):
            unit (Union[Unset, None, str]):
            window_seconds (Union[Unset, None, int]):
            file_name (Union[Unset, None, str]):
     """

    data_point_id: str
    separator: str
    version: int
    unit: Union[Unset, None, str] = UNSET
    window_seconds: Union[Unset, None, int] = UNSET
    file_name: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        data_point_id = self.data_point_id
        separator = self.separator
        version = self.version
        unit = self.unit
        window_seconds = self.window_seconds
        file_name = self.file_name

        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "dataPointId": data_point_id,
            "separator": separator,
            "version": version,
        })
        if unit is not UNSET:
            field_dict["unit"] = unit
        if window_seconds is not UNSET:
            field_dict["windowSeconds"] = window_seconds
        if file_name is not UNSET:
            field_dict["fileName"] = file_name

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_point_id = d.pop("dataPointId")

        separator = d.pop("separator")

        version = d.pop("version")

        unit = d.pop("unit", UNSET)

        window_seconds = d.pop("windowSeconds", UNSET)

        file_name = d.pop("fileName", UNSET)

        data_export_request = cls(
            data_point_id=data_point_id,
            separator=separator,
            version=version,
            unit=unit,
            window_seconds=window_seconds,
            file_name=file_name,
        )

        return data_export_request

