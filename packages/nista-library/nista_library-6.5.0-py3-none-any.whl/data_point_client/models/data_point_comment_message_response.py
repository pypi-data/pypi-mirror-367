from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import cast
from typing import Optional
import datetime
from typing import Union
from dateutil.parser import isoparse
from ..types import UNSET, Unset






T = TypeVar("T", bound="DataPointCommentMessageResponse")


@attr.s(auto_attribs=True)
class DataPointCommentMessageResponse:
    """ 
        Attributes:
            message_id (Union[Unset, str]):
            author (Union[Unset, None, str]):
            message (Union[Unset, None, str]):
            created (Union[Unset, datetime.datetime]):
            edited (Union[Unset, None, datetime.datetime]):
     """

    message_id: Union[Unset, str] = UNSET
    author: Union[Unset, None, str] = UNSET
    message: Union[Unset, None, str] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    edited: Union[Unset, None, datetime.datetime] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        message_id = self.message_id
        author = self.author
        message = self.message
        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        edited: Union[Unset, None, str] = UNSET
        if not isinstance(self.edited, Unset):
            edited = self.edited.isoformat() if self.edited else None


        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if message_id is not UNSET:
            field_dict["messageId"] = message_id
        if author is not UNSET:
            field_dict["author"] = author
        if message is not UNSET:
            field_dict["message"] = message
        if created is not UNSET:
            field_dict["created"] = created
        if edited is not UNSET:
            field_dict["edited"] = edited

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message_id = d.pop("messageId", UNSET)

        author = d.pop("author", UNSET)

        message = d.pop("message", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created,  Unset):
            created = UNSET
        else:
            created = isoparse(_created)




        _edited = d.pop("edited", UNSET)
        edited: Union[Unset, None, datetime.datetime]
        if _edited is None:
            edited = None
        elif isinstance(_edited,  Unset):
            edited = UNSET
        else:
            edited = isoparse(_edited)




        data_point_comment_message_response = cls(
            message_id=message_id,
            author=author,
            message=message,
            created=created,
            edited=edited,
        )

        return data_point_comment_message_response

