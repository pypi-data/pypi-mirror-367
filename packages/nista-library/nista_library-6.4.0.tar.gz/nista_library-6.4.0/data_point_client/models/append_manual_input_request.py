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
  from ..models.manual_input_request import ManualInputRequest





T = TypeVar("T", bound="AppendManualInputRequest")


@attr.s(auto_attribs=True)
class AppendManualInputRequest:
    """ 
        Attributes:
            manual_inputs (Union[Unset, None, List['ManualInputRequest']]):
            unit (Union[Unset, None, str]):
            time_zone (Union[Unset, None, str]):
     """

    manual_inputs: Union[Unset, None, List['ManualInputRequest']] = UNSET
    unit: Union[Unset, None, str] = UNSET
    time_zone: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.manual_input_request import ManualInputRequest
        manual_inputs: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.manual_inputs, Unset):
            if self.manual_inputs is None:
                manual_inputs = None
            else:
                manual_inputs = []
                for manual_inputs_item_data in self.manual_inputs:
                    manual_inputs_item = manual_inputs_item_data.to_dict()

                    manual_inputs.append(manual_inputs_item)




        unit = self.unit
        time_zone = self.time_zone

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if manual_inputs is not UNSET:
            field_dict["manualInputs"] = manual_inputs
        if unit is not UNSET:
            field_dict["unit"] = unit
        if time_zone is not UNSET:
            field_dict["timeZone"] = time_zone

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.manual_input_request import ManualInputRequest
        d = src_dict.copy()
        manual_inputs = []
        _manual_inputs = d.pop("manualInputs", UNSET)
        for manual_inputs_item_data in (_manual_inputs or []):
            manual_inputs_item = ManualInputRequest.from_dict(manual_inputs_item_data)



            manual_inputs.append(manual_inputs_item)


        unit = d.pop("unit", UNSET)

        time_zone = d.pop("timeZone", UNSET)

        append_manual_input_request = cls(
            manual_inputs=manual_inputs,
            unit=unit,
            time_zone=time_zone,
        )

        return append_manual_input_request

