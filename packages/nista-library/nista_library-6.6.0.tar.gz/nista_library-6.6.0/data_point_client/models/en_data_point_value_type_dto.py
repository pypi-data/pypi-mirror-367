from enum import Enum

class EnDataPointValueTypeDTO(str, Enum):
    FLUX = "Flux"
    INTEGRATED = "Integrated"
    STATE = "State"

    def __str__(self) -> str:
        return str(self.value)
