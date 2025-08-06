from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset






T = TypeVar("T", bound="GetQualityStatisticResponse")


@attr.s(auto_attribs=True)
class GetQualityStatisticResponse:
    """ 
        Attributes:
            elapsed_seconds_median (Union[Unset, int]):
            elapsed_seconds_mean (Union[Unset, int]):
     """

    elapsed_seconds_median: Union[Unset, int] = UNSET
    elapsed_seconds_mean: Union[Unset, int] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        elapsed_seconds_median = self.elapsed_seconds_median
        elapsed_seconds_mean = self.elapsed_seconds_mean

        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if elapsed_seconds_median is not UNSET:
            field_dict["elapsedSecondsMedian"] = elapsed_seconds_median
        if elapsed_seconds_mean is not UNSET:
            field_dict["elapsedSecondsMean"] = elapsed_seconds_mean

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        elapsed_seconds_median = d.pop("elapsedSecondsMedian", UNSET)

        elapsed_seconds_mean = d.pop("elapsedSecondsMean", UNSET)

        get_quality_statistic_response = cls(
            elapsed_seconds_median=elapsed_seconds_median,
            elapsed_seconds_mean=elapsed_seconds_mean,
        )

        return get_quality_statistic_response

