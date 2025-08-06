from enum import Enum

class EnDataPointStatus(str, Enum):
    ERROR = "Error"
    INCREATION = "InCreation"
    READY = "Ready"

    def __str__(self) -> str:
        return str(self.value)
