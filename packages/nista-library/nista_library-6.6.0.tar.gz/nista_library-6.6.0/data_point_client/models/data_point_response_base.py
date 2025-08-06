from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

import datetime
from ..models.en_data_point_value_type_dto import EnDataPointValueTypeDTO
from typing import Dict
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from ..models.en_data_point_state_dto import EnDataPointStateDTO
from typing import Union
from typing import cast
from typing import cast, List
from typing import Optional
from ..models.en_data_point_existence_dto import EnDataPointExistenceDTO

if TYPE_CHECKING:
  from ..models.data_bucket_base import DataBucketBase
  from ..models.data_point_origin import DataPointOrigin
  from ..models.data_point_info import DataPointInfo





T = TypeVar("T", bound="DataPointResponseBase")


@attr.s(auto_attribs=True)
class DataPointResponseBase:
    """ 
        Attributes:
            data_point_id (str):
            created_on (datetime.datetime):
            facility_id (Union[Unset, None, str]):
            name (Union[Unset, None, str]):
            description (Union[Unset, None, str]):
            created_by (Union[Unset, None, str]):
            tags (Union[Unset, None, List[str]]):
            data_point_info (Union[Unset, None, DataPointInfo]):
            store (Union[Unset, None, DataBucketBase]):
            state (Union[Unset, EnDataPointStateDTO]):
            existence (Union[Unset, EnDataPointExistenceDTO]):
            error_details (Union[Unset, None, str]):
            origin (Union[Unset, None, DataPointOrigin]):
            used_in_calculations (Union[Unset, None, List[str]]):
            used_in_reports (Union[Unset, None, List[str]]):
            used_in_analysis (Union[Unset, None, List[str]]):
            used_in_violation (Union[Unset, None, List[str]]):
            used_in_tasks (Union[Unset, None, List[str]]):
            base_64_thumbnail (Union[Unset, None, str]):
            significant_energy_use (Union[Unset, bool]):
            data_point_value_type (Union[Unset, None, EnDataPointValueTypeDTO]):
     """

    data_point_id: str
    created_on: datetime.datetime
    facility_id: Union[Unset, None, str] = UNSET
    name: Union[Unset, None, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    created_by: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    data_point_info: Union[Unset, None, 'DataPointInfo'] = UNSET
    store: Union[Unset, None, 'DataBucketBase'] = UNSET
    state: Union[Unset, EnDataPointStateDTO] = UNSET
    existence: Union[Unset, EnDataPointExistenceDTO] = UNSET
    error_details: Union[Unset, None, str] = UNSET
    origin: Union[Unset, None, 'DataPointOrigin'] = UNSET
    used_in_calculations: Union[Unset, None, List[str]] = UNSET
    used_in_reports: Union[Unset, None, List[str]] = UNSET
    used_in_analysis: Union[Unset, None, List[str]] = UNSET
    used_in_violation: Union[Unset, None, List[str]] = UNSET
    used_in_tasks: Union[Unset, None, List[str]] = UNSET
    base_64_thumbnail: Union[Unset, None, str] = UNSET
    significant_energy_use: Union[Unset, bool] = UNSET
    data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.data_bucket_base import DataBucketBase
        from ..models.data_point_origin import DataPointOrigin
        from ..models.data_point_info import DataPointInfo
        data_point_id = self.data_point_id
        created_on = self.created_on.isoformat()

        facility_id = self.facility_id
        name = self.name
        description = self.description
        created_by = self.created_by
        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags




        data_point_info: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.data_point_info, Unset):
            data_point_info = self.data_point_info.to_dict() if self.data_point_info else None

        store: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.store, Unset):
            store = self.store.to_dict() if self.store else None

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        existence: Union[Unset, str] = UNSET
        if not isinstance(self.existence, Unset):
            existence = self.existence.value

        error_details = self.error_details
        origin: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.to_dict() if self.origin else None

        used_in_calculations: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.used_in_calculations, Unset):
            if self.used_in_calculations is None:
                used_in_calculations = None
            else:
                used_in_calculations = self.used_in_calculations




        used_in_reports: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.used_in_reports, Unset):
            if self.used_in_reports is None:
                used_in_reports = None
            else:
                used_in_reports = self.used_in_reports




        used_in_analysis: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.used_in_analysis, Unset):
            if self.used_in_analysis is None:
                used_in_analysis = None
            else:
                used_in_analysis = self.used_in_analysis




        used_in_violation: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.used_in_violation, Unset):
            if self.used_in_violation is None:
                used_in_violation = None
            else:
                used_in_violation = self.used_in_violation




        used_in_tasks: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.used_in_tasks, Unset):
            if self.used_in_tasks is None:
                used_in_tasks = None
            else:
                used_in_tasks = self.used_in_tasks




        base_64_thumbnail = self.base_64_thumbnail
        significant_energy_use = self.significant_energy_use
        data_point_value_type: Union[Unset, None, str] = UNSET
        if not isinstance(self.data_point_value_type, Unset):
            data_point_value_type = self.data_point_value_type.value if self.data_point_value_type else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "dataPointId": data_point_id,
            "createdOn": created_on,
        })
        if facility_id is not UNSET:
            field_dict["facilityId"] = facility_id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if tags is not UNSET:
            field_dict["tags"] = tags
        if data_point_info is not UNSET:
            field_dict["dataPointInfo"] = data_point_info
        if store is not UNSET:
            field_dict["store"] = store
        if state is not UNSET:
            field_dict["state"] = state
        if existence is not UNSET:
            field_dict["existence"] = existence
        if error_details is not UNSET:
            field_dict["errorDetails"] = error_details
        if origin is not UNSET:
            field_dict["origin"] = origin
        if used_in_calculations is not UNSET:
            field_dict["usedInCalculations"] = used_in_calculations
        if used_in_reports is not UNSET:
            field_dict["usedInReports"] = used_in_reports
        if used_in_analysis is not UNSET:
            field_dict["usedInAnalysis"] = used_in_analysis
        if used_in_violation is not UNSET:
            field_dict["usedInViolation"] = used_in_violation
        if used_in_tasks is not UNSET:
            field_dict["usedInTasks"] = used_in_tasks
        if base_64_thumbnail is not UNSET:
            field_dict["base64Thumbnail"] = base_64_thumbnail
        if significant_energy_use is not UNSET:
            field_dict["significantEnergyUse"] = significant_energy_use
        if data_point_value_type is not UNSET:
            field_dict["dataPointValueType"] = data_point_value_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_bucket_base import DataBucketBase
        from ..models.data_point_origin import DataPointOrigin
        from ..models.data_point_info import DataPointInfo
        d = src_dict.copy()
        data_point_id = d.pop("dataPointId")

        created_on = isoparse(d.pop("createdOn"))




        facility_id = d.pop("facilityId", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        created_by = d.pop("createdBy", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))


        _data_point_info = d.pop("dataPointInfo", UNSET)
        data_point_info: Union[Unset, None, DataPointInfo]
        if _data_point_info is None:
            data_point_info = None
        elif isinstance(_data_point_info,  Unset):
            data_point_info = UNSET
        else:
            data_point_info = DataPointInfo.from_dict(_data_point_info)




        _store = d.pop("store", UNSET)
        store: Union[Unset, None, DataBucketBase]
        if _store is None:
            store = None
        elif isinstance(_store,  Unset):
            store = UNSET
        else:
            store = DataBucketBase.from_dict(_store)




        _state = d.pop("state", UNSET)
        state: Union[Unset, EnDataPointStateDTO]
        if isinstance(_state,  Unset):
            state = UNSET
        else:
            state = EnDataPointStateDTO(_state)




        _existence = d.pop("existence", UNSET)
        existence: Union[Unset, EnDataPointExistenceDTO]
        if isinstance(_existence,  Unset):
            existence = UNSET
        else:
            existence = EnDataPointExistenceDTO(_existence)




        error_details = d.pop("errorDetails", UNSET)

        _origin = d.pop("origin", UNSET)
        origin: Union[Unset, None, DataPointOrigin]
        if _origin is None:
            origin = None
        elif isinstance(_origin,  Unset):
            origin = UNSET
        else:
            origin = DataPointOrigin.from_dict(_origin)




        used_in_calculations = cast(List[str], d.pop("usedInCalculations", UNSET))


        used_in_reports = cast(List[str], d.pop("usedInReports", UNSET))


        used_in_analysis = cast(List[str], d.pop("usedInAnalysis", UNSET))


        used_in_violation = cast(List[str], d.pop("usedInViolation", UNSET))


        used_in_tasks = cast(List[str], d.pop("usedInTasks", UNSET))


        base_64_thumbnail = d.pop("base64Thumbnail", UNSET)

        significant_energy_use = d.pop("significantEnergyUse", UNSET)

        _data_point_value_type = d.pop("dataPointValueType", UNSET)
        data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO]
        if _data_point_value_type is None:
            data_point_value_type = None
        elif isinstance(_data_point_value_type,  Unset):
            data_point_value_type = UNSET
        else:
            data_point_value_type = EnDataPointValueTypeDTO(_data_point_value_type)




        data_point_response_base = cls(
            data_point_id=data_point_id,
            created_on=created_on,
            facility_id=facility_id,
            name=name,
            description=description,
            created_by=created_by,
            tags=tags,
            data_point_info=data_point_info,
            store=store,
            state=state,
            existence=existence,
            error_details=error_details,
            origin=origin,
            used_in_calculations=used_in_calculations,
            used_in_reports=used_in_reports,
            used_in_analysis=used_in_analysis,
            used_in_violation=used_in_violation,
            used_in_tasks=used_in_tasks,
            base_64_thumbnail=base_64_thumbnail,
            significant_energy_use=significant_energy_use,
            data_point_value_type=data_point_value_type,
        )

        return data_point_response_base

