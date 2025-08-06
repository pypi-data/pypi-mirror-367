from enum import Enum

class EnAreaTypeRest(str, Enum):
    ANOMALY = "Anomaly"
    COMMENT = "Comment"
    INSIGHT = "Insight"

    def __str__(self) -> str:
        return str(self.value)
