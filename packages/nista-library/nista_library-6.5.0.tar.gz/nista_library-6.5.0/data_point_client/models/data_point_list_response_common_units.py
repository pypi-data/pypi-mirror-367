from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.gnista_unit_response import GnistaUnitResponse





T = TypeVar("T", bound="DataPointListResponseCommonUnits")


@attr.s(auto_attribs=True)
class DataPointListResponseCommonUnits:
    """ 
     """

    additional_properties: Dict[str, 'GnistaUnitResponse'] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.gnista_unit_response import GnistaUnitResponse
        
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gnista_unit_response import GnistaUnitResponse
        d = src_dict.copy()
        data_point_list_response_common_units = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = GnistaUnitResponse.from_dict(prop_dict)



            additional_properties[prop_name] = additional_property

        data_point_list_response_common_units.additional_properties = additional_properties
        return data_point_list_response_common_units

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> 'GnistaUnitResponse':
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: 'GnistaUnitResponse') -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
