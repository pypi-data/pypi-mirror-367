from enum import Enum

class DecisionStrategy(str, Enum):
    AFFIRMATIVE = "AFFIRMATIVE"
    CONSENSUS = "CONSENSUS"
    UNANIMOUS = "UNANIMOUS"

    def __str__(self) -> str:
        return str(self.value)
