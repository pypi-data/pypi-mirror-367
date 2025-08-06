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
  from ..models.series_meta_data_response import SeriesMetaDataResponse
  from ..models.gnista_unit_response import GnistaUnitResponse
  from ..models.data_point_data_response import DataPointDataResponse
  from ..models.manual_input_response import ManualInputResponse
  from ..models.rule import Rule





T = TypeVar("T", bound="SeriesDataBucket")


@attr.s(auto_attribs=True)
class SeriesDataBucket:
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
            rules_for_cleanup (Union[Unset, None, List['Rule']]):
            first_entry (Union[Unset, datetime.datetime]):
            last_entry (Union[Unset, datetime.datetime]):
            time_zone (Union[Unset, None, str]):
            manual_inputs (Union[Unset, None, List['ManualInputResponse']]):
            meta_data (Union[Unset, None, SeriesMetaDataResponse]):
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
    rules_for_cleanup: Union[Unset, None, List['Rule']] = UNSET
    first_entry: Union[Unset, datetime.datetime] = UNSET
    last_entry: Union[Unset, datetime.datetime] = UNSET
    time_zone: Union[Unset, None, str] = UNSET
    manual_inputs: Union[Unset, None, List['ManualInputResponse']] = UNSET
    meta_data: Union[Unset, None, 'SeriesMetaDataResponse'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.series_meta_data_response import SeriesMetaDataResponse
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.data_point_data_response import DataPointDataResponse
        from ..models.manual_input_response import ManualInputResponse
        from ..models.rule import Rule
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




        rules_for_cleanup: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.rules_for_cleanup, Unset):
            if self.rules_for_cleanup is None:
                rules_for_cleanup = None
            else:
                rules_for_cleanup = []
                for rules_for_cleanup_item_data in self.rules_for_cleanup:
                    rules_for_cleanup_item = rules_for_cleanup_item_data.to_dict()

                    rules_for_cleanup.append(rules_for_cleanup_item)




        first_entry: Union[Unset, str] = UNSET
        if not isinstance(self.first_entry, Unset):
            first_entry = self.first_entry.isoformat()

        last_entry: Union[Unset, str] = UNSET
        if not isinstance(self.last_entry, Unset):
            last_entry = self.last_entry.isoformat()

        time_zone = self.time_zone
        manual_inputs: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.manual_inputs, Unset):
            if self.manual_inputs is None:
                manual_inputs = None
            else:
                manual_inputs = []
                for manual_inputs_item_data in self.manual_inputs:
                    manual_inputs_item = manual_inputs_item_data.to_dict()

                    manual_inputs.append(manual_inputs_item)




        meta_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.meta_data, Unset):
            meta_data = self.meta_data.to_dict() if self.meta_data else None


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
        if rules_for_cleanup is not UNSET:
            field_dict["rulesForCleanup"] = rules_for_cleanup
        if first_entry is not UNSET:
            field_dict["firstEntry"] = first_entry
        if last_entry is not UNSET:
            field_dict["lastEntry"] = last_entry
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if manual_inputs is not UNSET:
            field_dict["manualInputs"] = manual_inputs
        if meta_data is not UNSET:
            field_dict["metaData"] = meta_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.series_meta_data_response import SeriesMetaDataResponse
        from ..models.gnista_unit_response import GnistaUnitResponse
        from ..models.data_point_data_response import DataPointDataResponse
        from ..models.manual_input_response import ManualInputResponse
        from ..models.rule import Rule
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


        rules_for_cleanup = []
        _rules_for_cleanup = d.pop("rulesForCleanup", UNSET)
        for rules_for_cleanup_item_data in (_rules_for_cleanup or []):
            rules_for_cleanup_item = Rule.from_dict(rules_for_cleanup_item_data)



            rules_for_cleanup.append(rules_for_cleanup_item)


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




        time_zone = d.pop("timeZone", UNSET)

        manual_inputs = []
        _manual_inputs = d.pop("manualInputs", UNSET)
        for manual_inputs_item_data in (_manual_inputs or []):
            manual_inputs_item = ManualInputResponse.from_dict(manual_inputs_item_data)



            manual_inputs.append(manual_inputs_item)


        _meta_data = d.pop("metaData", UNSET)
        meta_data: Union[Unset, None, SeriesMetaDataResponse]
        if _meta_data is None:
            meta_data = None
        elif isinstance(_meta_data,  Unset):
            meta_data = UNSET
        else:
            meta_data = SeriesMetaDataResponse.from_dict(_meta_data)




        series_data_bucket = cls(
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
            rules_for_cleanup=rules_for_cleanup,
            first_entry=first_entry,
            last_entry=last_entry,
            time_zone=time_zone,
            manual_inputs=manual_inputs,
            meta_data=meta_data,
        )

        series_data_bucket.additional_properties = d
        return series_data_bucket

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
