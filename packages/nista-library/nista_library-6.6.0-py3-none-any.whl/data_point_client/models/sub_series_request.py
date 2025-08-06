from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import Optional

if TYPE_CHECKING:
  from ..models.sub_series_request_values import SubSeriesRequestValues





T = TypeVar("T", bound="SubSeriesRequest")


@attr.s(auto_attribs=True)
class SubSeriesRequest:
    """ 
        Attributes:
            values (Union[Unset, None, SubSeriesRequestValues]):
     """

    values: Union[Unset, None, 'SubSeriesRequestValues'] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.sub_series_request_values import SubSeriesRequestValues
        values: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.values, Unset):
            values = self.values.to_dict() if self.values else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sub_series_request_values import SubSeriesRequestValues
        d = src_dict.copy()
        _values = d.pop("values", UNSET)
        values: Union[Unset, None, SubSeriesRequestValues]
        if _values is None:
            values = None
        elif isinstance(_values,  Unset):
            values = UNSET
        else:
            values = SubSeriesRequestValues.from_dict(_values)




        sub_series_request = cls(
            values=values,
        )

        return sub_series_request

