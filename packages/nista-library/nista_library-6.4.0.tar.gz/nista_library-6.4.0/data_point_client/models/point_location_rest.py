from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from ..types import UNSET, Unset
from dateutil.parser import isoparse
import datetime
from typing import Union






T = TypeVar("T", bound="PointLocationRest")


@attr.s(auto_attribs=True)
class PointLocationRest:
    """ 
        Attributes:
            discriminator (str):
            at (Union[Unset, datetime.datetime]):
     """

    discriminator: str
    at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        at: Union[Unset, str] = UNSET
        if not isinstance(self.at, Unset):
            at = self.at.isoformat()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if at is not UNSET:
            field_dict["at"] = at

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _at = d.pop("at", UNSET)
        at: Union[Unset, datetime.datetime]
        if isinstance(_at,  Unset):
            at = UNSET
        else:
            at = isoparse(_at)




        point_location_rest = cls(
            discriminator=discriminator,
            at=at,
        )

        point_location_rest.additional_properties = d
        return point_location_rest

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
