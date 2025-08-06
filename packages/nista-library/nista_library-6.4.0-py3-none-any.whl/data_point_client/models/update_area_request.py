from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from ..models.en_area_type_rest import EnAreaTypeRest
from typing import Union

if TYPE_CHECKING:
  from ..models.location_rest import LocationRest





T = TypeVar("T", bound="UpdateAreaRequest")


@attr.s(auto_attribs=True)
class UpdateAreaRequest:
    """ 
        Attributes:
            type (Union[Unset, None, EnAreaTypeRest]):
            location (Union[Unset, None, LocationRest]):
            initial_message (Union[Unset, None, str]):
            is_open (Union[Unset, bool]):
     """

    type: Union[Unset, None, EnAreaTypeRest] = UNSET
    location: Union[Unset, None, 'LocationRest'] = UNSET
    initial_message: Union[Unset, None, str] = UNSET
    is_open: Union[Unset, bool] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.location_rest import LocationRest
        type: Union[Unset, None, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value if self.type else None

        location: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict() if self.location else None

        initial_message = self.initial_message
        is_open = self.is_open

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if type is not UNSET:
            field_dict["type"] = type
        if location is not UNSET:
            field_dict["location"] = location
        if initial_message is not UNSET:
            field_dict["initialMessage"] = initial_message
        if is_open is not UNSET:
            field_dict["isOpen"] = is_open

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.location_rest import LocationRest
        d = src_dict.copy()
        _type = d.pop("type", UNSET)
        type: Union[Unset, None, EnAreaTypeRest]
        if _type is None:
            type = None
        elif isinstance(_type,  Unset):
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




        initial_message = d.pop("initialMessage", UNSET)

        is_open = d.pop("isOpen", UNSET)

        update_area_request = cls(
            type=type,
            location=location,
            initial_message=initial_message,
            is_open=is_open,
        )

        return update_area_request

