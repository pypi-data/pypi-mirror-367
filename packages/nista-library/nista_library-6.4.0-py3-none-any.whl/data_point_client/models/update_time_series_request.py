from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from ..models.en_import_options import EnImportOptions
from ..models.en_data_point_value_type_dto import EnDataPointValueTypeDTO
from typing import Union

if TYPE_CHECKING:
  from ..models.sub_series_request import SubSeriesRequest





T = TypeVar("T", bound="UpdateTimeSeriesRequest")


@attr.s(auto_attribs=True)
class UpdateTimeSeriesRequest:
    """ 
        Attributes:
            execution_id (Union[Unset, None, str]):
            sub_series (Union[Unset, None, List['SubSeriesRequest']]):
            warnings (Union[Unset, None, List[str]]):
            unit (Union[Unset, None, str]):
            force_unit (Union[Unset, None, bool]):
            import_options (Union[Unset, EnImportOptions]):
            block_to_right (Union[Unset, bool]):
            time_zone (Union[Unset, None, str]):
            data_point_value_type (Union[Unset, None, EnDataPointValueTypeDTO]):
     """

    execution_id: Union[Unset, None, str] = UNSET
    sub_series: Union[Unset, None, List['SubSeriesRequest']] = UNSET
    warnings: Union[Unset, None, List[str]] = UNSET
    unit: Union[Unset, None, str] = UNSET
    force_unit: Union[Unset, None, bool] = UNSET
    import_options: Union[Unset, EnImportOptions] = UNSET
    block_to_right: Union[Unset, bool] = UNSET
    time_zone: Union[Unset, None, str] = UNSET
    data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.sub_series_request import SubSeriesRequest
        execution_id = self.execution_id
        sub_series: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sub_series, Unset):
            if self.sub_series is None:
                sub_series = None
            else:
                sub_series = []
                for sub_series_item_data in self.sub_series:
                    sub_series_item = sub_series_item_data.to_dict()

                    sub_series.append(sub_series_item)




        warnings: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.warnings, Unset):
            if self.warnings is None:
                warnings = None
            else:
                warnings = self.warnings




        unit = self.unit
        force_unit = self.force_unit
        import_options: Union[Unset, str] = UNSET
        if not isinstance(self.import_options, Unset):
            import_options = self.import_options.value

        block_to_right = self.block_to_right
        time_zone = self.time_zone
        data_point_value_type: Union[Unset, None, str] = UNSET
        if not isinstance(self.data_point_value_type, Unset):
            data_point_value_type = self.data_point_value_type.value if self.data_point_value_type else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if execution_id is not UNSET:
            field_dict["executionId"] = execution_id
        if sub_series is not UNSET:
            field_dict["subSeries"] = sub_series
        if warnings is not UNSET:
            field_dict["warnings"] = warnings
        if unit is not UNSET:
            field_dict["unit"] = unit
        if force_unit is not UNSET:
            field_dict["forceUnit"] = force_unit
        if import_options is not UNSET:
            field_dict["importOptions"] = import_options
        if block_to_right is not UNSET:
            field_dict["blockToRight"] = block_to_right
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if data_point_value_type is not UNSET:
            field_dict["dataPointValueType"] = data_point_value_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sub_series_request import SubSeriesRequest
        d = src_dict.copy()
        execution_id = d.pop("executionId", UNSET)

        sub_series = []
        _sub_series = d.pop("subSeries", UNSET)
        for sub_series_item_data in (_sub_series or []):
            sub_series_item = SubSeriesRequest.from_dict(sub_series_item_data)



            sub_series.append(sub_series_item)


        warnings = cast(List[str], d.pop("warnings", UNSET))


        unit = d.pop("unit", UNSET)

        force_unit = d.pop("forceUnit", UNSET)

        _import_options = d.pop("importOptions", UNSET)
        import_options: Union[Unset, EnImportOptions]
        if isinstance(_import_options,  Unset):
            import_options = UNSET
        else:
            import_options = EnImportOptions(_import_options)




        block_to_right = d.pop("blockToRight", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        _data_point_value_type = d.pop("dataPointValueType", UNSET)
        data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO]
        if _data_point_value_type is None:
            data_point_value_type = None
        elif isinstance(_data_point_value_type,  Unset):
            data_point_value_type = UNSET
        else:
            data_point_value_type = EnDataPointValueTypeDTO(_data_point_value_type)




        update_time_series_request = cls(
            execution_id=execution_id,
            sub_series=sub_series,
            warnings=warnings,
            unit=unit,
            force_unit=force_unit,
            import_options=import_options,
            block_to_right=block_to_right,
            time_zone=time_zone,
            data_point_value_type=data_point_value_type,
        )

        return update_time_series_request

