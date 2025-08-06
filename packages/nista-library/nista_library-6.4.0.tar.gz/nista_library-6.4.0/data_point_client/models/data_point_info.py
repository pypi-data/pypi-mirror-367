from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Optional






T = TypeVar("T", bound="DataPointInfo")


@attr.s(auto_attribs=True)
class DataPointInfo:
    """ 
        Attributes:
            direction (Union[Unset, None, str]):
            range_ (Union[Unset, None, str]):
            aggregation (Union[Unset, None, str]):
            medium (Union[Unset, None, str]):
            group (Union[Unset, None, str]):
     """

    direction: Union[Unset, None, str] = UNSET
    range_: Union[Unset, None, str] = UNSET
    aggregation: Union[Unset, None, str] = UNSET
    medium: Union[Unset, None, str] = UNSET
    group: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        direction = self.direction
        range_ = self.range_
        aggregation = self.aggregation
        medium = self.medium
        group = self.group

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if direction is not UNSET:
            field_dict["direction"] = direction
        if range_ is not UNSET:
            field_dict["range"] = range_
        if aggregation is not UNSET:
            field_dict["aggregation"] = aggregation
        if medium is not UNSET:
            field_dict["medium"] = medium
        if group is not UNSET:
            field_dict["group"] = group

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        direction = d.pop("direction", UNSET)

        range_ = d.pop("range", UNSET)

        aggregation = d.pop("aggregation", UNSET)

        medium = d.pop("medium", UNSET)

        group = d.pop("group", UNSET)

        data_point_info = cls(
            direction=direction,
            range_=range_,
            aggregation=aggregation,
            medium=medium,
            group=group,
        )

        return data_point_info

