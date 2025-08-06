from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
from typing import Dict
from ..models.en_area_type_rest import EnAreaTypeRest
from typing import Union
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.location_rest import LocationRest





T = TypeVar("T", bound="CreateAreaRequest")


@attr.s(auto_attribs=True)
class CreateAreaRequest:
    """ 
        Attributes:
            type (Union[Unset, EnAreaTypeRest]):
            location (Union[Unset, None, LocationRest]):
            initial_message (Union[Unset, None, str]):
     """

    type: Union[Unset, EnAreaTypeRest] = UNSET
    location: Union[Unset, None, 'LocationRest'] = UNSET
    initial_message: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.location_rest import LocationRest
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        location: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict() if self.location else None

        initial_message = self.initial_message

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if type is not UNSET:
            field_dict["type"] = type
        if location is not UNSET:
            field_dict["location"] = location
        if initial_message is not UNSET:
            field_dict["initialMessage"] = initial_message

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.location_rest import LocationRest
        d = src_dict.copy()
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




        initial_message = d.pop("initialMessage", UNSET)

        create_area_request = cls(
            type=type,
            location=location,
            initial_message=initial_message,
        )

        return create_area_request

