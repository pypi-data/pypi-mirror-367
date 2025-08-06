from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import cast
from ..types import UNSET, Unset
from dateutil.parser import isoparse
import datetime
from typing import Union






T = TypeVar("T", bound="ContinuousLocationRest")


@attr.s(auto_attribs=True)
class ContinuousLocationRest:
    """ 
        Attributes:
            discriminator (str):
            from_ (Union[Unset, datetime.datetime]):
            to (Union[Unset, datetime.datetime]):
     """

    discriminator: str
    from_: Union[Unset, datetime.datetime] = UNSET
    to: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        from_: Union[Unset, str] = UNSET
        if not isinstance(self.from_, Unset):
            from_ = self.from_.isoformat()

        to: Union[Unset, str] = UNSET
        if not isinstance(self.to, Unset):
            to = self.to.isoformat()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

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




        continuous_location_rest = cls(
            discriminator=discriminator,
            from_=from_,
            to=to,
        )

        continuous_location_rest.additional_properties = d
        return continuous_location_rest

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
