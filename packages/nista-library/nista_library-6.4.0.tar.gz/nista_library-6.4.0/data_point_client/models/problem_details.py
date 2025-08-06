from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import Optional
from typing import cast
from ..types import UNSET, Unset
from typing import Union

if TYPE_CHECKING:
  from ..models.problem_details_extensions import ProblemDetailsExtensions





T = TypeVar("T", bound="ProblemDetails")


@attr.s(auto_attribs=True)
class ProblemDetails:
    """ 
        Attributes:
            type (Union[Unset, None, str]):
            title (Union[Unset, None, str]):
            status (Union[Unset, None, int]):
            detail (Union[Unset, None, str]):
            instance (Union[Unset, None, str]):
            extensions (Union[Unset, ProblemDetailsExtensions]):
     """

    type: Union[Unset, None, str] = UNSET
    title: Union[Unset, None, str] = UNSET
    status: Union[Unset, None, int] = UNSET
    detail: Union[Unset, None, str] = UNSET
    instance: Union[Unset, None, str] = UNSET
    extensions: Union[Unset, 'ProblemDetailsExtensions'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.problem_details_extensions import ProblemDetailsExtensions
        type = self.type
        title = self.title
        status = self.status
        detail = self.detail
        instance = self.instance
        extensions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if type is not UNSET:
            field_dict["type"] = type
        if title is not UNSET:
            field_dict["title"] = title
        if status is not UNSET:
            field_dict["status"] = status
        if detail is not UNSET:
            field_dict["detail"] = detail
        if instance is not UNSET:
            field_dict["instance"] = instance
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.problem_details_extensions import ProblemDetailsExtensions
        d = src_dict.copy()
        type = d.pop("type", UNSET)

        title = d.pop("title", UNSET)

        status = d.pop("status", UNSET)

        detail = d.pop("detail", UNSET)

        instance = d.pop("instance", UNSET)

        _extensions = d.pop("extensions", UNSET)
        extensions: Union[Unset, ProblemDetailsExtensions]
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = ProblemDetailsExtensions.from_dict(_extensions)




        problem_details = cls(
            type=type,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            extensions=extensions,
        )


        problem_details.additional_properties = d
        return problem_details

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
