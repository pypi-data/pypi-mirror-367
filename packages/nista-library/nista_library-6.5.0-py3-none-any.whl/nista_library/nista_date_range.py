from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from data_point_client.models import DateRangeDTO


class NistaDateRange:

    first_entry: datetime
    last_entry: datetime

    def __init__(self, first_entry: datetime, last_entry: datetime):
        self.first_entry = first_entry
        self.last_entry = last_entry

    def to_data_range_dto(self, time_zone: ZoneInfo):
        first_entry = self.to_utc(self.first_entry, time_zone)
        last_entry = self.to_utc(self.last_entry, time_zone)
        return DateRangeDTO(first_entry=first_entry, last_entry=last_entry)

    @staticmethod
    def to_utc(entry: datetime, time_zone: ZoneInfo) -> datetime:
        entry_with_time_zone = entry.replace(tzinfo=time_zone)
        utc_time = entry_with_time_zone.astimezone(timezone.utc)
        return utc_time
