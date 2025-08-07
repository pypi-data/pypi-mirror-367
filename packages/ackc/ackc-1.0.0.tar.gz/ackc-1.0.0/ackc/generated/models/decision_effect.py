from enum import Enum

class DecisionEffect(str, Enum):
    DENY = "DENY"
    PERMIT = "PERMIT"

    def __str__(self) -> str:
        return str(self.value)
