from enum import Enum

class EnDataBucketState(str, Enum):
    ERROR = "Error"
    INPROGRESS = "InProgress"
    READY = "Ready"

    def __str__(self) -> str:
        return str(self.value)
