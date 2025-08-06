from enum import Enum

class EnOperator(str, Enum):
    EQUAL = "Equal"
    LARGER = "Larger"
    SMALLER = "Smaller"

    def __str__(self) -> str:
        return str(self.value)
