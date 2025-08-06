from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING


import attr

from ..types import UNSET, Unset

from typing import Dict
from ..types import UNSET, Unset
from typing import Union
from typing import cast
from typing import cast, List
from typing import Optional

if TYPE_CHECKING:
  from ..models.quarterly_comparison_cache_response import QuarterlyComparisonCacheResponse
  from ..models.last_month_cache_response import LastMonthCacheResponse
  from ..models.last_week_cache_response import LastWeekCacheResponse
  from ..models.last_7_days_cache_response import Last7DaysCacheResponse
  from ..models.day_meta_data_response import DayMetaDataResponse
  from ..models.yearly_comparison_response import YearlyComparisonResponse





T = TypeVar("T", bound="SeriesMetaDataResponse")


@attr.s(auto_attribs=True)
class SeriesMetaDataResponse:
    """ 
        Attributes:
            minimum (Union[Unset, None, float]):
            maximum (Union[Unset, None, float]):
            mean (Union[Unset, None, float]):
            baseload (Union[Unset, None, float]):
            year_to_date_dataquality (Union[Unset, None, float]):
            interval_mean (Union[Unset, None, float]):
            last_week_cache (Union[Unset, None, LastWeekCacheResponse]):
            last_7_days_cache (Union[Unset, None, Last7DaysCacheResponse]):
            last_month_cache (Union[Unset, None, LastMonthCacheResponse]):
            quarterly_comparison_cache (Union[Unset, None, QuarterlyComparisonCacheResponse]):
            yearly_comparison_cache (Union[Unset, None, YearlyComparisonResponse]):
            last_years_daily_sums (Union[Unset, None, List['DayMetaDataResponse']]):
     """

    minimum: Union[Unset, None, float] = UNSET
    maximum: Union[Unset, None, float] = UNSET
    mean: Union[Unset, None, float] = UNSET
    baseload: Union[Unset, None, float] = UNSET
    year_to_date_dataquality: Union[Unset, None, float] = UNSET
    interval_mean: Union[Unset, None, float] = UNSET
    last_week_cache: Union[Unset, None, 'LastWeekCacheResponse'] = UNSET
    last_7_days_cache: Union[Unset, None, 'Last7DaysCacheResponse'] = UNSET
    last_month_cache: Union[Unset, None, 'LastMonthCacheResponse'] = UNSET
    quarterly_comparison_cache: Union[Unset, None, 'QuarterlyComparisonCacheResponse'] = UNSET
    yearly_comparison_cache: Union[Unset, None, 'YearlyComparisonResponse'] = UNSET
    last_years_daily_sums: Union[Unset, None, List['DayMetaDataResponse']] = UNSET


    def to_dict(self) -> Dict[str, Any]:
        from ..models.quarterly_comparison_cache_response import QuarterlyComparisonCacheResponse
        from ..models.last_month_cache_response import LastMonthCacheResponse
        from ..models.last_week_cache_response import LastWeekCacheResponse
        from ..models.last_7_days_cache_response import Last7DaysCacheResponse
        from ..models.day_meta_data_response import DayMetaDataResponse
        from ..models.yearly_comparison_response import YearlyComparisonResponse
        minimum = self.minimum
        maximum = self.maximum
        mean = self.mean
        baseload = self.baseload
        year_to_date_dataquality = self.year_to_date_dataquality
        interval_mean = self.interval_mean
        last_week_cache: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.last_week_cache, Unset):
            last_week_cache = self.last_week_cache.to_dict() if self.last_week_cache else None

        last_7_days_cache: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.last_7_days_cache, Unset):
            last_7_days_cache = self.last_7_days_cache.to_dict() if self.last_7_days_cache else None

        last_month_cache: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.last_month_cache, Unset):
            last_month_cache = self.last_month_cache.to_dict() if self.last_month_cache else None

        quarterly_comparison_cache: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.quarterly_comparison_cache, Unset):
            quarterly_comparison_cache = self.quarterly_comparison_cache.to_dict() if self.quarterly_comparison_cache else None

        yearly_comparison_cache: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.yearly_comparison_cache, Unset):
            yearly_comparison_cache = self.yearly_comparison_cache.to_dict() if self.yearly_comparison_cache else None

        last_years_daily_sums: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.last_years_daily_sums, Unset):
            if self.last_years_daily_sums is None:
                last_years_daily_sums = None
            else:
                last_years_daily_sums = []
                for last_years_daily_sums_item_data in self.last_years_daily_sums:
                    last_years_daily_sums_item = last_years_daily_sums_item_data.to_dict()

                    last_years_daily_sums.append(last_years_daily_sums_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update({
        })
        if minimum is not UNSET:
            field_dict["minimum"] = minimum
        if maximum is not UNSET:
            field_dict["maximum"] = maximum
        if mean is not UNSET:
            field_dict["mean"] = mean
        if baseload is not UNSET:
            field_dict["baseload"] = baseload
        if year_to_date_dataquality is not UNSET:
            field_dict["yearToDateDataquality"] = year_to_date_dataquality
        if interval_mean is not UNSET:
            field_dict["intervalMean"] = interval_mean
        if last_week_cache is not UNSET:
            field_dict["lastWeekCache"] = last_week_cache
        if last_7_days_cache is not UNSET:
            field_dict["last7DaysCache"] = last_7_days_cache
        if last_month_cache is not UNSET:
            field_dict["lastMonthCache"] = last_month_cache
        if quarterly_comparison_cache is not UNSET:
            field_dict["quarterlyComparisonCache"] = quarterly_comparison_cache
        if yearly_comparison_cache is not UNSET:
            field_dict["yearlyComparisonCache"] = yearly_comparison_cache
        if last_years_daily_sums is not UNSET:
            field_dict["lastYearsDailySums"] = last_years_daily_sums

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.quarterly_comparison_cache_response import QuarterlyComparisonCacheResponse
        from ..models.last_month_cache_response import LastMonthCacheResponse
        from ..models.last_week_cache_response import LastWeekCacheResponse
        from ..models.last_7_days_cache_response import Last7DaysCacheResponse
        from ..models.day_meta_data_response import DayMetaDataResponse
        from ..models.yearly_comparison_response import YearlyComparisonResponse
        d = src_dict.copy()
        minimum = d.pop("minimum", UNSET)

        maximum = d.pop("maximum", UNSET)

        mean = d.pop("mean", UNSET)

        baseload = d.pop("baseload", UNSET)

        year_to_date_dataquality = d.pop("yearToDateDataquality", UNSET)

        interval_mean = d.pop("intervalMean", UNSET)

        _last_week_cache = d.pop("lastWeekCache", UNSET)
        last_week_cache: Union[Unset, None, LastWeekCacheResponse]
        if _last_week_cache is None:
            last_week_cache = None
        elif isinstance(_last_week_cache,  Unset):
            last_week_cache = UNSET
        else:
            last_week_cache = LastWeekCacheResponse.from_dict(_last_week_cache)




        _last_7_days_cache = d.pop("last7DaysCache", UNSET)
        last_7_days_cache: Union[Unset, None, Last7DaysCacheResponse]
        if _last_7_days_cache is None:
            last_7_days_cache = None
        elif isinstance(_last_7_days_cache,  Unset):
            last_7_days_cache = UNSET
        else:
            last_7_days_cache = Last7DaysCacheResponse.from_dict(_last_7_days_cache)




        _last_month_cache = d.pop("lastMonthCache", UNSET)
        last_month_cache: Union[Unset, None, LastMonthCacheResponse]
        if _last_month_cache is None:
            last_month_cache = None
        elif isinstance(_last_month_cache,  Unset):
            last_month_cache = UNSET
        else:
            last_month_cache = LastMonthCacheResponse.from_dict(_last_month_cache)




        _quarterly_comparison_cache = d.pop("quarterlyComparisonCache", UNSET)
        quarterly_comparison_cache: Union[Unset, None, QuarterlyComparisonCacheResponse]
        if _quarterly_comparison_cache is None:
            quarterly_comparison_cache = None
        elif isinstance(_quarterly_comparison_cache,  Unset):
            quarterly_comparison_cache = UNSET
        else:
            quarterly_comparison_cache = QuarterlyComparisonCacheResponse.from_dict(_quarterly_comparison_cache)




        _yearly_comparison_cache = d.pop("yearlyComparisonCache", UNSET)
        yearly_comparison_cache: Union[Unset, None, YearlyComparisonResponse]
        if _yearly_comparison_cache is None:
            yearly_comparison_cache = None
        elif isinstance(_yearly_comparison_cache,  Unset):
            yearly_comparison_cache = UNSET
        else:
            yearly_comparison_cache = YearlyComparisonResponse.from_dict(_yearly_comparison_cache)




        last_years_daily_sums = []
        _last_years_daily_sums = d.pop("lastYearsDailySums", UNSET)
        for last_years_daily_sums_item_data in (_last_years_daily_sums or []):
            last_years_daily_sums_item = DayMetaDataResponse.from_dict(last_years_daily_sums_item_data)



            last_years_daily_sums.append(last_years_daily_sums_item)


        series_meta_data_response = cls(
            minimum=minimum,
            maximum=maximum,
            mean=mean,
            baseload=baseload,
            year_to_date_dataquality=year_to_date_dataquality,
            interval_mean=interval_mean,
            last_week_cache=last_week_cache,
            last_7_days_cache=last_7_days_cache,
            last_month_cache=last_month_cache,
            quarterly_comparison_cache=quarterly_comparison_cache,
            yearly_comparison_cache=yearly_comparison_cache,
            last_years_daily_sums=last_years_daily_sums,
        )

        return series_meta_data_response

