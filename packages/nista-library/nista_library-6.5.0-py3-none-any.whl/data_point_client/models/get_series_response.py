from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
from typing import cast, List
from typing import Union
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.time_series_response import TimeSeriesResponse





T = TypeVar("T", bound="GetSeriesResponse")


@attr.s(auto_attribs=True)
class GetSeriesResponse:
    """ 
        Attributes:
            discriminator (str):
            curves (Union[Unset, None, List['TimeSeriesResponse']]):
            time_zone (Union[Unset, None, str]):
            unit (Union[Unset, None, str]):
     """

    discriminator: str
    curves: Union[Unset, None, List['TimeSeriesResponse']] = UNSET
    time_zone: Union[Unset, None, str] = UNSET
    unit: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_series_response import TimeSeriesResponse
        discriminator = self.discriminator
        curves: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.curves, Unset):
            if self.curves is None:
                curves = None
            else:
                curves = []
                for curves_item_data in self.curves:
                    curves_item = curves_item_data.to_dict()

                    curves.append(curves_item)




        time_zone = self.time_zone
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if curves is not UNSET:
            field_dict["curves"] = curves
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_response import TimeSeriesResponse
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        curves = []
        _curves = d.pop("curves", UNSET)
        for curves_item_data in (_curves or []):
            curves_item = TimeSeriesResponse.from_dict(curves_item_data)



            curves.append(curves_item)


        time_zone = d.pop("timeZone", UNSET)

        unit = d.pop("unit", UNSET)

        get_series_response = cls(
            discriminator=discriminator,
            curves=curves,
            time_zone=time_zone,
            unit=unit,
        )

        get_series_response.additional_properties = d
        return get_series_response

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
