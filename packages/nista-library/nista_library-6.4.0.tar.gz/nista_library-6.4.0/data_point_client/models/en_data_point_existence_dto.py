from enum import Enum

class EnDataPointExistenceDTO(str, Enum):
    DELETED = "Deleted"
    FULL = "Full"
    HIDDEN = "Hidden"
    LOW = "Low"

    def __str__(self) -> str:
        return str(self.value)
