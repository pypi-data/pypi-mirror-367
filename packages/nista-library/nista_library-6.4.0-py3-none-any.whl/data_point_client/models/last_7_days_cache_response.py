from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast, List
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from typing import Union

if TYPE_CHECKING:
  from ..models.last_7_days_meta_data_response import Last7DaysMetaDataResponse





T = TypeVar("T", bound="Last7DaysCacheResponse")


@attr.s(auto_attribs=True)
class Last7DaysCacheResponse:
    """ 
        Attributes:
            last_7_days (Union[Unset, None, List['Last7DaysMetaDataResponse']]):
     """

    last_7_days: Union[Unset, None, List['Last7DaysMetaDataResponse']] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.last_7_days_meta_data_response import Last7DaysMetaDataResponse
        last_7_days: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.last_7_days, Unset):
            if self.last_7_days is None:
                last_7_days = None
            else:
                last_7_days = []
                for last_7_days_item_data in self.last_7_days:
                    last_7_days_item = last_7_days_item_data.to_dict()

                    last_7_days.append(last_7_days_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if last_7_days is not UNSET:
            field_dict["last7Days"] = last_7_days

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.last_7_days_meta_data_response import Last7DaysMetaDataResponse
        d = src_dict.copy()
        last_7_days = []
        _last_7_days = d.pop("last7Days", UNSET)
        for last_7_days_item_data in (_last_7_days or []):
            last_7_days_item = Last7DaysMetaDataResponse.from_dict(last_7_days_item_data)



            last_7_days.append(last_7_days_item)


        last_7_days_cache_response = cls(
            last_7_days=last_7_days,
        )

        return last_7_days_cache_response

