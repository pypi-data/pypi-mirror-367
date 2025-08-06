from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import cast, List
from typing import Optional

if TYPE_CHECKING:
  from ..models.data_point_response_base import DataPointResponseBase
  from ..models.data_point_list_response_common_units import DataPointListResponseCommonUnits





T = TypeVar("T", bound="DataPointListResponse")


@attr.s(auto_attribs=True)
class DataPointListResponse:
    """ 
        Attributes:
            data_points (Union[Unset, None, List['DataPointResponseBase']]):
            common_units (Union[Unset, None, DataPointListResponseCommonUnits]):
     """

    data_points: Union[Unset, None, List['DataPointResponseBase']] = UNSET
    common_units: Union[Unset, None, 'DataPointListResponseCommonUnits'] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.data_point_response_base import DataPointResponseBase
        from ..models.data_point_list_response_common_units import DataPointListResponseCommonUnits
        data_points: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.data_points, Unset):
            if self.data_points is None:
                data_points = None
            else:
                data_points = []
                for data_points_item_data in self.data_points:
                    data_points_item = data_points_item_data.to_dict()

                    data_points.append(data_points_item)




        common_units: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.common_units, Unset):
            common_units = self.common_units.to_dict() if self.common_units else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if data_points is not UNSET:
            field_dict["dataPoints"] = data_points
        if common_units is not UNSET:
            field_dict["commonUnits"] = common_units

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_point_response_base import DataPointResponseBase
        from ..models.data_point_list_response_common_units import DataPointListResponseCommonUnits
        d = src_dict.copy()
        data_points = []
        _data_points = d.pop("dataPoints", UNSET)
        for data_points_item_data in (_data_points or []):
            data_points_item = DataPointResponseBase.from_dict(data_points_item_data)



            data_points.append(data_points_item)


        _common_units = d.pop("commonUnits", UNSET)
        common_units: Union[Unset, None, DataPointListResponseCommonUnits]
        if _common_units is None:
            common_units = None
        elif isinstance(_common_units,  Unset):
            common_units = UNSET
        else:
            common_units = DataPointListResponseCommonUnits.from_dict(_common_units)




        data_point_list_response = cls(
            data_points=data_points,
            common_units=common_units,
        )

        return data_point_list_response

