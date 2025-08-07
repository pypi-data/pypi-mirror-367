from enum import Enum

class BruteForceStrategy(str, Enum):
    LINEAR = "LINEAR"
    MULTIPLE = "MULTIPLE"

    def __str__(self) -> str:
        return str(self.value)
