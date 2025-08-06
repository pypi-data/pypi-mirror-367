from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Union
from typing import Optional
from ..types import UNSET, Unset






T = TypeVar("T", bound="CreateAreaMessageRequest")


@attr.s(auto_attribs=True)
class CreateAreaMessageRequest:
    """ 
        Attributes:
            reply_message (Union[Unset, None, str]):
     """

    reply_message: Union[Unset, None, str] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        reply_message = self.reply_message

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if reply_message is not UNSET:
            field_dict["replyMessage"] = reply_message

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        reply_message = d.pop("replyMessage", UNSET)

        create_area_message_request = cls(
            reply_message=reply_message,
        )

        return create_area_message_request

