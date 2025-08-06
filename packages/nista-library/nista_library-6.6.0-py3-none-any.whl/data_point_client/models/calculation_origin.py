from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Optional
from typing import Union
from ..types import UNSET, Unset






T = TypeVar("T", bound="CalculationOrigin")


@attr.s(auto_attribs=True)
class CalculationOrigin:
    """ 
        Attributes:
            discriminator (str):
            calculation_id (Union[Unset, None, str]):
     """

    discriminator: str
    calculation_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        calculation_id = self.calculation_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if calculation_id is not UNSET:
            field_dict["calculationId"] = calculation_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        calculation_id = d.pop("calculationId", UNSET)

        calculation_origin = cls(
            discriminator=discriminator,
            calculation_id=calculation_id,
        )

        calculation_origin.additional_properties = d
        return calculation_origin

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
