from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset







T = TypeVar("T", bound="DataPointOrigin")


@attr.s(auto_attribs=True)
class DataPointOrigin:
    """ 
        Attributes:
            discriminator (str):
     """

    discriminator: str


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator

        field_dict: Dict[str, Any] = {}
        field_dict.update({
            "discriminator": discriminator,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        data_point_origin = cls(
            discriminator=discriminator,
        )

        return data_point_origin

