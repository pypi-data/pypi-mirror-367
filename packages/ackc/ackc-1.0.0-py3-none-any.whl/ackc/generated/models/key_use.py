from enum import Enum

class KeyUse(str, Enum):
    ENC = "ENC"
    SIG = "SIG"

    def __str__(self) -> str:
        return str(self.value)
