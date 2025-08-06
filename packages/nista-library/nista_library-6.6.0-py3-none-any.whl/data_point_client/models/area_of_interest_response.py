from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import cast, List
from typing import Optional
from ..models.en_area_type_rest import EnAreaTypeRest

if TYPE_CHECKING:
  from ..models.location_rest import LocationRest
  from ..models.data_point_comment_message_response import DataPointCommentMessageResponse





T = TypeVar("T", bound="AreaOfInterestResponse")


@attr.s(auto_attribs=True)
class AreaOfInterestResponse:
    """ 
        Attributes:
            area_id (Union[Unset, str]):
            type (Union[Unset, EnAreaTypeRest]):
            location (Union[Unset, None, LocationRest]):
            is_open (Union[Unset, bool]):
            initial (Union[Unset, None, DataPointCommentMessageResponse]):
            replies (Union[Unset, None, List['DataPointCommentMessageResponse']]):
     """

    area_id: Union[Unset, str] = UNSET
    type: Union[Unset, EnAreaTypeRest] = UNSET
    location: Union[Unset, None, 'LocationRest'] = UNSET
    is_open: Union[Unset, bool] = UNSET
    initial: Union[Unset, None, 'DataPointCommentMessageResponse'] = UNSET
    replies: Union[Unset, None, List['DataPointCommentMessageResponse']] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.location_rest import LocationRest
        from ..models.data_point_comment_message_response import DataPointCommentMessageResponse
        area_id = self.area_id
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        location: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict() if self.location else None

        is_open = self.is_open
        initial: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.initial, Unset):
            initial = self.initial.to_dict() if self.initial else None

        replies: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.replies, Unset):
            if self.replies is None:
                replies = None
            else:
                replies = []
                for replies_item_data in self.replies:
                    replies_item = replies_item_data.to_dict()

                    replies.append(replies_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if area_id is not UNSET:
            field_dict["areaId"] = area_id
        if type is not UNSET:
            field_dict["type"] = type
        if location is not UNSET:
            field_dict["location"] = location
        if is_open is not UNSET:
            field_dict["isOpen"] = is_open
        if initial is not UNSET:
            field_dict["initial"] = initial
        if replies is not UNSET:
            field_dict["replies"] = replies

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.location_rest import LocationRest
        from ..models.data_point_comment_message_response import DataPointCommentMessageResponse
        d = src_dict.copy()
        area_id = d.pop("areaId", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, EnAreaTypeRest]
        if isinstance(_type,  Unset):
            type = UNSET
        else:
            type = EnAreaTypeRest(_type)




        _location = d.pop("location", UNSET)
        location: Union[Unset, None, LocationRest]
        if _location is None:
            location = None
        elif isinstance(_location,  Unset):
            location = UNSET
        else:
            location = LocationRest.from_dict(_location)




        is_open = d.pop("isOpen", UNSET)

        _initial = d.pop("initial", UNSET)
        initial: Union[Unset, None, DataPointCommentMessageResponse]
        if _initial is None:
            initial = None
        elif isinstance(_initial,  Unset):
            initial = UNSET
        else:
            initial = DataPointCommentMessageResponse.from_dict(_initial)




        replies = []
        _replies = d.pop("replies", UNSET)
        for replies_item_data in (_replies or []):
            replies_item = DataPointCommentMessageResponse.from_dict(replies_item_data)



            replies.append(replies_item)


        area_of_interest_response = cls(
            area_id=area_id,
            type=type,
            location=location,
            is_open=is_open,
            initial=initial,
            replies=replies,
        )

        return area_of_interest_response

