import json
import uuid
from datetime import timezone
from http import HTTPStatus
from typing import Any, List, Optional, Type, TypeVar, Union
from zoneinfo import ZoneInfo

import pandas as pd
from pandas import DataFrame
from structlog import get_logger

from data_point_client import AuthenticatedClient
from data_point_client.api.data_point import (
    data_point_append_execution_result_data,
    data_point_append_time_series_data,
    data_point_create_data_point,
    data_point_finish_execution_result_data,
    data_point_get_data,
    data_point_get_data_point,
    data_point_update_constant_data,
    data_point_update_time_series_data,
    data_point_update_week_period_data,
    data_point_update_data_point,
    data_point_get_data_quality,
    data_point_get_quality_statistic,
)
from data_point_client.models import GetConstantResponse, GetSeriesResponse
from data_point_client.models.append_execution_result_data_request import (
    AppendExecutionResultDataRequest,
)
from data_point_client.models.append_time_series_request import AppendTimeSeriesRequest
from data_point_client.models.constant_data_bucket import ConstantDataBucket
from data_point_client.models.data_point_request import DataPointRequest
from data_point_client.models.data_point_response_base import DataPointResponseBase
from data_point_client.models.day_data_base_transfer import DayDataBaseTransfer
from data_point_client.models.day_period_data_bucket import DayPeriodDataBucket
from data_point_client.models.en_data_point_existence_dto import EnDataPointExistenceDTO
from data_point_client.models.en_data_point_value_type_dto import EnDataPointValueTypeDTO
from data_point_client.models.en_import_options import EnImportOptions
from data_point_client.models.finish_execution_result_data_request import FinishExecutionResultDataRequest
from data_point_client.models.get_data_quality_request import GetDataQualityRequest
from data_point_client.models.get_data_request import GetDataRequest
from data_point_client.models.get_day_period_response import GetDayPeriodResponse
from data_point_client.models.get_quality_statistic_response import GetQualityStatisticResponse
from data_point_client.models.get_week_period_response import GetWeekPeriodResponse
from data_point_client.models.problem_details import ProblemDetails
from data_point_client.models.series_data_bucket import SeriesDataBucket
from data_point_client.models.sub_series_request import SubSeriesRequest
from data_point_client.models.sub_series_request_values import SubSeriesRequestValues
from data_point_client.models.time_series_quality_response_curve import TimeSeriesQualityResponseCurve
from data_point_client.models.time_series_response_curve import TimeSeriesResponseCurve
from data_point_client.models.update_constant_data_request import (
    UpdateConstantDataRequest,
)
from data_point_client.models.update_time_series_request import UpdateTimeSeriesRequest
from data_point_client.models.update_week_period_request import UpdateWeekPeriodRequest
from data_point_client.models.week_data_transfere import WeekDataTransfere
from data_point_client.models.week_period_data_bucket import WeekPeriodDataBucket
from data_point_client.types import UNSET, Response, Unset
from nista_library.nista_connetion import NistaConnection
from nista_library.nista_date_range import NistaDateRange

log = get_logger()

# pylint: disable=C0103
T = TypeVar("T", bound="NistaDataPoint")


class NistaDataPoint:
    """Represents a DataPoint from nista.io
    :DATE_FORMAT: Format to use for parse dictionaries
    :DATE_NAME: Column Name for Dates
    :VALUE_NAME: Column Name for Value
    """

    DATE_NAME = "Date"
    VALUE_NAME = "Value"

    _data_point_response: Optional[DataPointResponseBase] = None
    _store: Union[SeriesDataBucket, ConstantDataBucket, WeekPeriodDataBucket, DayPeriodDataBucket, None] = None

    loaded = False

    @property
    def data_point_response(self) -> Optional[DataPointResponseBase]:
        """Loads and interprets the DataPoint if it has not bee loaded.
        :returns: The DataPoint Details from nista.io
        """
        if self._data_point_response is None:
            self._load_details()
        return self._data_point_response

    @property
    def store(self) -> Union[SeriesDataBucket, ConstantDataBucket, WeekPeriodDataBucket, DayPeriodDataBucket, None]:
        """Loads and interprets the DataPoint if it has not bee loaded.
        :returns: The DataPoint Details from nista.io
        """
        if self._store is None:
            self._load_details()
        return self._store

    @classmethod
    def create_new(
        cls: Type[T], connection: NistaConnection, name: str, tags: List[str], new_id: Optional[str] = None
    ) -> Optional[T]:
        """Creates a new DataPoint in nista.io
        :param connection: To be used to connecto to nista.io
        :param name: The new name of the DataPoint
        :param tags: List of Tags to add to the new DataPoint
        :param new_id: The ID to use for the datapoint
        :returns: The created DataPoint
        """

        token = connection.get_access_token()
        client = AuthenticatedClient(
            base_url=connection.datapoint_base_url,
            token=token,
            verify_ssl=connection.verify_ssl,
        )

        if new_id is None:
            new_id = str(uuid.uuid4())

        request = DataPointRequest(name=name, description="", existence=EnDataPointExistenceDTO.FULL, tags=tags)

        response = data_point_create_data_point.sync(
            client=client,
            data_point_id=new_id,
            workspace_id=connection.workspace_id,
            json_body=request,
        )

        if isinstance(response, ProblemDetails):
            log.error(response)
            return None

        data_point = cls(connection=connection, data_point_id=new_id, name=name)
        return data_point

    def __init__(
        self,
        connection: NistaConnection,
        data_point_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Load a DataPoint from nista.io
        :param connection: To be used to connecto to nista.io
        :param data_point_id: The Unique ID to load the DataPoint
        :param name: Optional Name to use for this DataPoint
        """

        self.connection = connection
        self.data_point_id = data_point_id
        if name is None:
            self._load_details()
        else:
            self.name = name
            self.description = description

    def __str__(self):
        return "NistaDataPoint " + str(self.data_point_id) + " with name " + self.name

    def _load_details(self):
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
        )

        response_content = data_point_get_data_point.sync_detailed(
            client=client,
            data_point_id=self.data_point_id,
            workspace_id=self.connection.workspace_id,
        )

        content_text = response_content.content.decode("utf-8")

        if (
            response_content.parsed is None
            or response_content.status_code == HTTPStatus.NOT_FOUND
            or response_content.status_code == HTTPStatus.FORBIDDEN
        ):
            self._data_point_response = None
            self.name = None
            self.description = None
            self.loaded = False
            return

        if isinstance(response_content.parsed, ProblemDetails):
            log.error(content_text)
            raise ValueError("Cannot load Datapoint")

        jscon_content = json.loads(content_text)
        data_point = DataPointResponseBase.from_dict(jscon_content)

        if data_point is None:
            raise ValueError("Cannot load Datapoint")

        self._store = None
        if data_point.store is not None:
            discriminator = data_point.store.discriminator

            if discriminator == "ConstantDataBucket":
                self._store = ConstantDataBucket.from_dict(jscon_content["store"])
            elif discriminator == "SeriesDataBucket":
                self._store = SeriesDataBucket.from_dict(jscon_content["store"])
            elif discriminator == "DayPeriodDataBucket":
                self._store = DayPeriodDataBucket.from_dict(jscon_content["store"])
            elif discriminator == "WeekPeriodDataBucket":
                self._store = WeekPeriodDataBucket.from_dict(jscon_content["store"])

            if self._store is not None:
                data_point.store = self._store

        self._data_point_response = data_point
        self.name = self.data_point_response.name
        self.description = self.data_point_response.description
        self.loaded = True

    def get_data_point_quality(
        self,
        request: GetDataQualityRequest,
        timeout: float = 30,
    ) -> Union[List[DataFrame], None]:
        """Retrieves the Quality Metric from a DataPoint
        :param request: Request details for retrieving Data Quality
        :param timeout: How long to wait for response
        :return: The DataPoint Quality Metric
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        series_response = data_point_get_data_quality.sync(
            client=client,
            data_point_id=self.data_point_id,
            workspace_id=self.connection.workspace_id,
            json_body=request,
        )

        if series_response is None:
            raise ValueError("Cannot load Datapoint")

        if isinstance(series_response, ProblemDetails):
            log.error(series_response.detail)
            raise ValueError("Cannot load Datapoint")

        curves = series_response.curves

        if request.remove_time_zone:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
        else:
            date_format = "%Y-%m-%dT%H:%M:%S%z"

        if isinstance(curves, list):
            data_frames = []
            # pylint: disable=E1133
            for curve in curves:
                # pylint: enable=E1133
                curve_dict = curve.curve
                if isinstance(curve_dict, TimeSeriesQualityResponseCurve):
                    data_frame = self._from_time_frames(
                        time_frames=curve_dict.to_dict(),
                        post_fix=False,
                        date_format=date_format,
                    )
                    data_frames.append(data_frame)

            return data_frames

        return None

    def get_data_point_quality_statistic(
        self,
        request: GetDataQualityRequest,
        timeout: float = 30,
    ) -> Union[GetQualityStatisticResponse, None]:
        """Retrieves the Quality Metric Statistic from a DataPoint
        :param request: Request details for retrieving Data Quality
        :param timeout: How long to wait for response
        :return: The DataPoint Quality Metric
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        series_response = data_point_get_quality_statistic.sync(
            client=client,
            data_point_id=self.data_point_id,
            workspace_id=self.connection.workspace_id,
            json_body=request,
        )

        if series_response is None:
            raise ValueError("Cannot load Datapoint")

        if isinstance(series_response, ProblemDetails):
            log.error(series_response.detail)
            raise ValueError("Cannot load Datapoint")

        return series_response

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-branches
    def get_data_point_data(
        self,
        request: GetDataRequest,
        post_fix: bool = False,
        timeout: float = 30,
    ) -> Union[List[DataFrame], float, Unset, WeekDataTransfere, DayDataBaseTransfer, None]:
        """Retrieves the Data from a DataPoint
        :param request: Request details for retrieving Data
        :param post_fix: Append nista.io instance name after DataPoint Name
        :param timeout: How long to wait for response
        :return: The DataPoint Data
        """

        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        response_content = data_point_get_data.sync_detailed(
            client=client,
            data_point_id=str(self.data_point_id),
            workspace_id=self.connection.workspace_id,
            json_body=request,
        )

        content_text = response_content.content.decode("utf-8")

        if isinstance(response_content.parsed, ProblemDetails):
            log.error(content_text)
            raise ValueError("Cannot load Datapoint")

        log.debug("Received Response from nista.io", content=content_text)

        jscon_content = json.loads(content_text)
        content_type = jscon_content["discriminator"]

        if content_type == "GetSeriesResponse":
            series_response = GetSeriesResponse.from_dict(jscon_content)
            curves = series_response.curves

            if request.remove_time_zone:
                date_format = "%Y-%m-%dT%H:%M:%SZ"
            else:
                date_format = "%Y-%m-%dT%H:%M:%S%z"

            if isinstance(curves, list):
                data_frames = []
                # pylint: disable=E1133
                for curve in curves:
                    # pylint: enable=E1133
                    curve_dict = curve.curve
                    if isinstance(curve_dict, TimeSeriesResponseCurve):
                        data_frame = self._from_time_frames(
                            time_frames=curve_dict.to_dict(), post_fix=post_fix, date_format=date_format
                        )
                        if not data_frame.empty:
                            data_frames.append(data_frame)

                return data_frames

        if content_type == "GetConstantResponse":
            constant_response = GetConstantResponse.from_dict(jscon_content)
            if constant_response is not None:
                return constant_response.value

        if content_type == "GetWeekPeriodResponse":
            week_response = GetWeekPeriodResponse.from_dict(jscon_content)
            if week_response is not None:
                return week_response.week_data

        if content_type == "GetDayPeriodResponse":
            day_response = GetDayPeriodResponse.from_dict(jscon_content)
            if day_response is not None:
                return day_response.day_data

        return None

    def append_data_point_data(
        self,
        data: Union[List[DataFrame], float],
        unit: Optional[str] = None,
        timeout: float = 5.0,
        time_zone: ZoneInfo = ZoneInfo("UTC"),
        import_options: Optional[EnImportOptions] = None,
        block_to_right: Optional[bool] = None,
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Append data to an existing DataPoint
        :param data: To be added to a DataPoint
        :param unit: The Unit to set on the DataPoint Store
        :param timeout: How long to wait for response
        :param time_zone: The Time Zone of the newly added Data, default is UTC
        """

        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            for data_frame in data:
                data_dict = self._to_dict(data_frame=data_frame, time_zone=time_zone)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            append_request = AppendTimeSeriesRequest(
                sub_series=sub_series,
                unit=unit,
                time_zone=time_zone.key,
                import_options=import_options if import_options is not None else UNSET,
                block_to_right=block_to_right if block_to_right is not None else UNSET,
            )

            return data_point_append_time_series_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=append_request,
            )

        return None

    def finish_append_result_parts(
        self,
        unit: Optional[str],
        execution_id: uuid.UUID,
        data_interval_in_seconds: int,
        timeout: float = 5.0,
        time_zone: ZoneInfo = ZoneInfo("UTC"),
        is_major_change: bool = False,
        sub_series_ranges: Optional[List[NistaDateRange]] = None,
        data_point_value_type: Optional[EnDataPointValueTypeDTO] = None
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Append data as an execution Result. This method is used for nista.io Internal Execution handling
        :param unit: The Unit to set on the DataPoint Store
        :param execution_id: the execution ID that this data is assignable to
        :param timeout: How long to wait for response
        :param time_zone: The Time Zone of the newly added Data, default is UTC
        :param is_major_change: Indicates if it is a major or minor change
        :param sub_series_ranges: Defines the subseries of the result
        :param data_interval_in_seconds: Defines the normal interval within the subseries
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        sub_series_as_data_range_dto = None
        if sub_series_ranges is not None:
            sub_series_as_data_range_dto = [
                sub_series_range.to_data_range_dto(time_zone) for sub_series_range in sub_series_ranges
            ]

        append_request = FinishExecutionResultDataRequest(
            unit=unit,
            time_zone=time_zone.key,
            is_major_change=is_major_change,
            sub_series=sub_series_as_data_range_dto,
            data_interval_in_seconds=data_interval_in_seconds,
            data_point_value_type=data_point_value_type
        )

        return data_point_finish_execution_result_data.sync_detailed(
            workspace_id=self.connection.workspace_id,
            execution_id=str(execution_id),
            client=client,
            data_point_id=str(self.data_point_id),
            json_body=append_request,
        )

    def append_data_point_result_parts(
        self,
        data: Union[List[DataFrame], float],
        execution_id: uuid.UUID,
        timeout: float = 5.0,
        time_zone: ZoneInfo = ZoneInfo("UTC"),
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Append data as an execution Result. This method is used for nista.io Internal Execution handling
        :param data: To be added to a DataPoint
        :param unit: The Unit to set on the DataPoint Store
        :param execution_id: the execution ID that this data is assignable to
        :param timeout: How long to wait for response
        :param time_zone: The Time Zone of the newly added Data, default is UTC
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            for data_frame in data:
                data_dict = self._to_dict(data_frame=data_frame, time_zone=time_zone)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            append_request = AppendExecutionResultDataRequest(
                sub_series=sub_series,
            )

            return data_point_append_execution_result_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                execution_id=str(execution_id),
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=append_request,
            )

        return None

    def set_data_point_data(
        self,
        data: Union[List[DataFrame], float, WeekDataTransfere],
        unit: Optional[str] = None,
        execution_id: Optional[str] = None,
        time_zone: ZoneInfo = ZoneInfo("UTC"),
        import_options: Optional[EnImportOptions] = None,
        block_to_right: Optional[bool] = None,
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Replace or Set DataPoint Data with new Data. This bumps the DataPoint Version
        :param data: To be added to a DataPoint
        :param unit: The Unit to set on the DataPoint Store
        :param execution_id: the execution ID that this data is assignable to
        :param time_zone: The Time Zone of the newly added Data
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
        )

        if isinstance(data, WeekDataTransfere):
            week_update_request = UpdateWeekPeriodRequest(
                execution_id=execution_id,
                unit=unit,
                week_data=data,
            )
            return data_point_update_week_period_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=week_update_request,
            )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []

            for data_frame in data:
                data_dict = self._to_dict(data_frame=data_frame, time_zone=time_zone)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            timeseries_update_request = UpdateTimeSeriesRequest(
                sub_series=sub_series,
                unit=unit,
                execution_id=execution_id,
                time_zone=time_zone.key,
                import_options=import_options if import_options is not None else UNSET,
                block_to_right=block_to_right if block_to_right is not None else UNSET,
            )

            return data_point_update_time_series_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=timeseries_update_request,
            )

        if isinstance(data, float):
            constant_request = UpdateConstantDataRequest(
                value=data,
                unit=unit,
                execution_id=execution_id,
            )

            return data_point_update_constant_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=constant_request,
            )

        return None

    def set_data_point_details(self, request: DataPointRequest):
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
        )

        data_point_update_data_point.sync(
            workspace_id=self.connection.workspace_id,
            client=client,
            data_point_id=str(self.data_point_id),
            json_body=request,
        )

    def _to_dict(self, data_frame: DataFrame, time_zone: ZoneInfo):
        result = {}
        dct = data_frame.to_dict()[self.VALUE_NAME]
        for key in dct.keys():
            if pd.isna(key):
                continue
            value = dct[key]
            zone = key.replace(tzinfo=time_zone)
            zone = zone.astimezone(timezone.utc)
            key_string = zone.strftime("%Y-%m-%dT%H:%M:%SZ")
            result[key_string] = value
        return result

    def _from_time_frames(self, time_frames: dict, post_fix: bool, date_format: str) -> DataFrame:
        if not isinstance(time_frames, dict):
            raise TypeError

        value_column_name = self.name

        if value_column_name is None:
            value_column_name = self.VALUE_NAME

        if post_fix:
            value_column_name = value_column_name + "_nista.io_" + str(self.data_point_id)

        log.debug("Reading data as Pandas DataFrame")

        data_record = []
        for date in time_frames:
            value = time_frames[date]
            data_record.append({self.DATE_NAME: date, value_column_name: value})

        data_frame = pd.DataFrame.from_records(data_record, columns=[self.DATE_NAME, value_column_name])

        data_frame[self.DATE_NAME] = pd.to_datetime(data_frame[self.DATE_NAME], format=date_format)

        data_frame[value_column_name] = pd.to_numeric(data_frame[value_column_name])

        data_frame.set_index(data_frame[self.DATE_NAME], inplace=True)
        data_frame.drop([self.DATE_NAME], axis=1, inplace=True)

        return data_frame
