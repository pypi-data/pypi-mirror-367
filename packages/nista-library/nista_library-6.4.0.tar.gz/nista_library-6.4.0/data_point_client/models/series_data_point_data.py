from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Optional






T = TypeVar("T", bound="SeriesDataPointData")


@attr.s(auto_attribs=True)
class SeriesDataPointData:
    """ 
        Attributes:
            discriminator (str):
            status (Union[Unset, None, str]):
            error_message (Union[Unset, None, str]):
            unit (Union[Unset, None, str]):
            number_of_entries (Union[Unset, int]):
            time_series_id (Union[Unset, None, str]):
            bucket_id (Union[Unset, None, str]):
     """

    discriminator: str
    status: Union[Unset, None, str] = UNSET
    error_message: Union[Unset, None, str] = UNSET
    unit: Union[Unset, None, str] = UNSET
    number_of_entries: Union[Unset, int] = UNSET
    time_series_id: Union[Unset, None, str] = UNSET
    bucket_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        status = self.status
        error_message = self.error_message
        unit = self.unit
        number_of_entries = self.number_of_entries
        time_series_id = self.time_series_id
        bucket_id = self.bucket_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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
        if time_series_id is not UNSET:
            field_dict["timeSeriesId"] = time_series_id
        if bucket_id is not UNSET:
            field_dict["bucketId"] = bucket_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        status = d.pop("status", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        unit = d.pop("unit", UNSET)

        number_of_entries = d.pop("numberOfEntries", UNSET)

        time_series_id = d.pop("timeSeriesId", UNSET)

        bucket_id = d.pop("bucketId", UNSET)

        series_data_point_data = cls(
            discriminator=discriminator,
            status=status,
            error_message=error_message,
            unit=unit,
            number_of_entries=number_of_entries,
            time_series_id=time_series_id,
            bucket_id=bucket_id,
        )

        series_data_point_data.additional_properties = d
        return series_data_point_data

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
