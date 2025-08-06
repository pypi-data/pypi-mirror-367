from enum import Enum

class EnDataPointType(str, Enum):
    CALCULATIONDATAPOINT = "CalculationDataPoint"
    IMPORTDATAPOINT = "ImportDataPoint"
    REMOTEDATAPOINT = "RemoteDataPoint"

    def __str__(self) -> str:
        return str(self.value)
