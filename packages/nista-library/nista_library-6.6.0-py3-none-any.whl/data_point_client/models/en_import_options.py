from enum import Enum

class EnImportOptions(str, Enum):
    AUTOMATIC = "Automatic"
    BLOCKVALUES = "BlockValues"
    BUILDDIFFERENTIAL = "BuildDifferential"
    RAW = "Raw"

    def __str__(self) -> str:
        return str(self.value)
