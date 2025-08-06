from enum import Enum

class EnDataPointStateDTO(str, Enum):
    DRAFT = "Draft"
    ERROR = "Error"
    INPROGRESS = "InProgress"
    READY = "Ready"

    def __str__(self) -> str:
        return str(self.value)
