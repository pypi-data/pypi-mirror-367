from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..models.en_data_point_value_type_dto import EnDataPointValueTypeDTO
from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import cast, List
from ..models.en_import_options import EnImportOptions
from typing import Optional

if TYPE_CHECKING:
  from ..models.sub_series_request import SubSeriesRequest





T = TypeVar("T", bound="AppendTimeSeriesRequest")


@attr.s(auto_attribs=True)
class AppendTimeSeriesRequest:
    """ 
        Attributes:
            sub_series (List['SubSeriesRequest']):
            unit (Union[Unset, None, str]):
            import_options (Union[Unset, EnImportOptions]):
            data_point_value_type (Union[Unset, None, EnDataPointValueTypeDTO]):
            block_to_right (Union[Unset, bool]):
            time_zone (Union[Unset, None, str]):
            cumulative_sensor_data (Union[Unset, bool]):
     """

    sub_series: List['SubSeriesRequest']
    unit: Union[Unset, None, str] = UNSET
    import_options: Union[Unset, EnImportOptions] = UNSET
    data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO] = UNSET
    block_to_right: Union[Unset, bool] = UNSET
    time_zone: Union[Unset, None, str] = UNSET
    cumulative_sensor_data: Union[Unset, bool] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.sub_series_request import SubSeriesRequest
        sub_series = []
        for sub_series_item_data in self.sub_series:
            sub_series_item = sub_series_item_data.to_dict()

            sub_series.append(sub_series_item)




        unit = self.unit
        import_options: Union[Unset, str] = UNSET
        if not isinstance(self.import_options, Unset):
            import_options = self.import_options.value

        data_point_value_type: Union[Unset, None, str] = UNSET
        if not isinstance(self.data_point_value_type, Unset):
            data_point_value_type = self.data_point_value_type.value if self.data_point_value_type else None

        block_to_right = self.block_to_right
        time_zone = self.time_zone
        cumulative_sensor_data = self.cumulative_sensor_data

        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "subSeries": sub_series,
        })
        if unit is not UNSET:
            field_dict["unit"] = unit
        if import_options is not UNSET:
            field_dict["importOptions"] = import_options
        if data_point_value_type is not UNSET:
            field_dict["dataPointValueType"] = data_point_value_type
        if block_to_right is not UNSET:
            field_dict["blockToRight"] = block_to_right
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if cumulative_sensor_data is not UNSET:
            field_dict["cumulativeSensorData"] = cumulative_sensor_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sub_series_request import SubSeriesRequest
        d = src_dict.copy()
        sub_series = []
        _sub_series = d.pop("subSeries")
        for sub_series_item_data in (_sub_series):
            sub_series_item = SubSeriesRequest.from_dict(sub_series_item_data)



            sub_series.append(sub_series_item)


        unit = d.pop("unit", UNSET)

        _import_options = d.pop("importOptions", UNSET)
        import_options: Union[Unset, EnImportOptions]
        if isinstance(_import_options,  Unset):
            import_options = UNSET
        else:
            import_options = EnImportOptions(_import_options)




        _data_point_value_type = d.pop("dataPointValueType", UNSET)
        data_point_value_type: Union[Unset, None, EnDataPointValueTypeDTO]
        if _data_point_value_type is None:
            data_point_value_type = None
        elif isinstance(_data_point_value_type,  Unset):
            data_point_value_type = UNSET
        else:
            data_point_value_type = EnDataPointValueTypeDTO(_data_point_value_type)




        block_to_right = d.pop("blockToRight", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        cumulative_sensor_data = d.pop("cumulativeSensorData", UNSET)

        append_time_series_request = cls(
            sub_series=sub_series,
            unit=unit,
            import_options=import_options,
            data_point_value_type=data_point_value_type,
            block_to_right=block_to_right,
            time_zone=time_zone,
            cumulative_sensor_data=cumulative_sensor_data,
        )

        return append_time_series_request

