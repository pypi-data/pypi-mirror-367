from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
import datetime
from typing import Union
from dateutil.parser import isoparse
from ..types import UNSET, Unset






T = TypeVar("T", bound="ManualInputRequest")


@attr.s(auto_attribs=True)
class ManualInputRequest:
    """ 
        Attributes:
            from_ (Union[Unset, datetime.datetime]):
            to (Union[Unset, datetime.datetime]):
            cumulative_value (Union[Unset, float]):
            sub_series_id (Union[Unset, None, str]):
     """

    from_: Union[Unset, datetime.datetime] = UNSET
    to: Union[Unset, datetime.datetime] = UNSET
    cumulative_value: Union[Unset, float] = UNSET
    sub_series_id: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from_: Union[Unset, str] = UNSET
        if not isinstance(self.from_, Unset):
            from_ = self.from_.isoformat()

        to: Union[Unset, str] = UNSET
        if not isinstance(self.to, Unset):
            to = self.to.isoformat()

        cumulative_value = self.cumulative_value
        sub_series_id = self.sub_series_id

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to
        if cumulative_value is not UNSET:
            field_dict["cumulativeValue"] = cumulative_value
        if sub_series_id is not UNSET:
            field_dict["subSeriesId"] = sub_series_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _from_ = d.pop("from", UNSET)
        from_: Union[Unset, datetime.datetime]
        if isinstance(_from_,  Unset):
            from_ = UNSET
        else:
            from_ = isoparse(_from_)




        _to = d.pop("to", UNSET)
        to: Union[Unset, datetime.datetime]
        if isinstance(_to,  Unset):
            to = UNSET
        else:
            to = isoparse(_to)




        cumulative_value = d.pop("cumulativeValue", UNSET)

        sub_series_id = d.pop("subSeriesId", UNSET)

        manual_input_request = cls(
            from_=from_,
            to=to,
            cumulative_value=cumulative_value,
            sub_series_id=sub_series_id,
        )

        return manual_input_request

