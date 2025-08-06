from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union
from typing import Optional






T = TypeVar("T", bound="FileOrigin")


@attr.s(auto_attribs=True)
class FileOrigin:
    """ 
        Attributes:
            discriminator (str):
            file_id (Union[Unset, None, str]):
            file_name (Union[Unset, None, str]):
            task_config_id (Union[Unset, None, str]):
     """

    discriminator: str
    file_id: Union[Unset, None, str] = UNSET
    file_name: Union[Unset, None, str] = UNSET
    task_config_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        file_id = self.file_id
        file_name = self.file_name
        task_config_id = self.task_config_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "discriminator": discriminator,
        })
        if file_id is not UNSET:
            field_dict["fileId"] = file_id
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if task_config_id is not UNSET:
            field_dict["taskConfigId"] = task_config_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        file_id = d.pop("fileId", UNSET)

        file_name = d.pop("fileName", UNSET)

        task_config_id = d.pop("taskConfigId", UNSET)

        file_origin = cls(
            discriminator=discriminator,
            file_id=file_id,
            file_name=file_name,
            task_config_id=task_config_id,
        )

        file_origin.additional_properties = d
        return file_origin

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
