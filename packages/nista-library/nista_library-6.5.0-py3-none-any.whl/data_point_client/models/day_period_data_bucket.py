from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
from ..models.en_data_bucket_state import EnDataBucketState
import datetime
from typing import cast, List
from typing import Union
from dateutil.parser import isoparse
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.gnista_unit_response import GnistaUnitResponse
  from ..models.day_period_data_point_data import DayPeriodDataPointData
  from ..models.data_point_data_response import DataPointDataResponse





T = TypeVar("T", bound="DayPeriodDataBucket")


@attr.s(auto_attribs=True)
class DayPeriodDataBucket:
    """ 
        Attributes:
            discriminator (str):
            version (Union[Unset, int]):
            minor_version (Union[Unset, int]):
            created (Union[Unset, datetime.datetime]):
            status (Union[Unset, EnDataBucketState]):
            violations (Union[Unset, int]):
            unit (Union[Unset, None, str]):
            preferred_unit (Union[Unset, None, str]):
            gnista_unit (Union[Unset, None, GnistaUnitResponse]):
            preferred_gnista_unit (Union[Unset, None, GnistaUnitResponse]):
            error_details (Union[Unset, None, str]):
            warning_details (Union[Unset, None, str]):
            available_data_points (Union[Unset, None, List['DataPointDataResponse']]):
            value (Union[Unset, None, List['DayPeriodDataPointData']]):
     """

    discriminator: str
    version: Union[Unset, int] = UNSET
    minor_version: Union[Unset, int] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, EnDataBucketState] = UNSET
    violations: Union[Unset, int] = UNSET
    unit: Union[Unset, None, str] = UNSET
    preferred_unit: Union[Unset, None, str] = UNSET
    gnista_unit: Union[Unset, None, 'GnistaUnitResponse'] = UNSET
    preferred_gnista_unit: Union[Unset, None, 'GnistaUnitResponse'] = UNSET
    error_details: Union[Unset, None, str] = UNSET
    warning_details: Union[Unset, None, str] = UNSET
    available_data_points: Union[Unset, None, List['DataPointDataResponse']] = UNSET
    value: Union[Unset, None, List['DayPeriodDataPointData']] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.day_period_data_point_data import DayPeriodDataPointData
        from ..models.data_point_data_response import DataPointDataResponse
        discriminator = self.discriminator
        version = self.version
        minor_version = self.minor_version
        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        violations = self.violations
        unit = self.unit
        preferred_unit = self.preferred_unit
        gnista_unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.gnista_unit, Unset):
            gnista_unit = self.gnista_unit.to_dict() if self.gnista_unit else None

        preferred_gnista_unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.preferred_gnista_unit, Unset):
            preferred_gnista_unit = self.preferred_gnista_unit.to_dict() if self.preferred_gnista_unit else None

        error_details = self.error_details
        warning_details = self.warning_details
        available_data_points: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.available_data_points, Unset):
            if self.available_data_points is None:
                available_data_points = None
            else:
                available_data_points = []
                for available_data_points_item_data in self.available_data_points:
                    available_data_points_item = available_data_points_item_data.to_dict()

                    available_data_points.append(available_data_points_item)




        value: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.value, Unset):
            if self.value is None:
                value = None
            else:
                value = []
                for value_item_data in self.value:
                    value_item = value_item_data.to_dict()

                    value.append(value_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if version is not UNSET:
            field_dict["version"] = version
        if minor_version is not UNSET:
            field_dict["minorVersion"] = minor_version
        if created is not UNSET:
            field_dict["created"] = created
        if status is not UNSET:
            field_dict["status"] = status
        if violations is not UNSET:
            field_dict["violations"] = violations
        if unit is not UNSET:
            field_dict["unit"] = unit
        if preferred_unit is not UNSET:
            field_dict["preferredUnit"] = preferred_unit
        if gnista_unit is not UNSET:
            field_dict["gnistaUnit"] = gnista_unit
        if preferred_gnista_unit is not UNSET:
            field_dict["preferredGnistaUnit"] = preferred_gnista_unit
        if error_details is not UNSET:
            field_dict["errorDetails"] = error_details
        if warning_details is not UNSET:
            field_dict["warningDetails"] = warning_details
        if available_data_points is not UNSET:
            field_dict["availableDataPoints"] = available_data_points
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.day_period_data_point_data import DayPeriodDataPointData
        from ..models.data_point_data_response import DataPointDataResponse
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        version = d.pop("version", UNSET)

        minor_version = d.pop("minorVersion", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created,  Unset):
            created = UNSET
        else:
            created = isoparse(_created)




        _status = d.pop("status", UNSET)
        status: Union[Unset, EnDataBucketState]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = EnDataBucketState(_status)




        violations = d.pop("violations", UNSET)

        unit = d.pop("unit", UNSET)

        preferred_unit = d.pop("preferredUnit", UNSET)

        _gnista_unit = d.pop("gnistaUnit", UNSET)
        gnista_unit: Union[Unset, None, GnistaUnitResponse]
        if _gnista_unit is None:
            gnista_unit = None
        elif isinstance(_gnista_unit,  Unset):
            gnista_unit = UNSET
        else:
            gnista_unit = GnistaUnitResponse.from_dict(_gnista_unit)




        _preferred_gnista_unit = d.pop("preferredGnistaUnit", UNSET)
        preferred_gnista_unit: Union[Unset, None, GnistaUnitResponse]
        if _preferred_gnista_unit is None:
            preferred_gnista_unit = None
        elif isinstance(_preferred_gnista_unit,  Unset):
            preferred_gnista_unit = UNSET
        else:
            preferred_gnista_unit = GnistaUnitResponse.from_dict(_preferred_gnista_unit)




        error_details = d.pop("errorDetails", UNSET)

        warning_details = d.pop("warningDetails", UNSET)

        available_data_points = []
        _available_data_points = d.pop("availableDataPoints", UNSET)
        for available_data_points_item_data in (_available_data_points or []):
            available_data_points_item = DataPointDataResponse.from_dict(available_data_points_item_data)



            available_data_points.append(available_data_points_item)


        value = []
        _value = d.pop("value", UNSET)
        for value_item_data in (_value or []):
            value_item = DayPeriodDataPointData.from_dict(value_item_data)



            value.append(value_item)


        day_period_data_bucket = cls(
            discriminator=discriminator,
            version=version,
            minor_version=minor_version,
            created=created,
            status=status,
            violations=violations,
            unit=unit,
            preferred_unit=preferred_unit,
            gnista_unit=gnista_unit,
            preferred_gnista_unit=preferred_gnista_unit,
            error_details=error_details,
            warning_details=warning_details,
            available_data_points=available_data_points,
            value=value,
        )

        day_period_data_bucket.additional_properties = d
        return day_period_data_bucket

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
