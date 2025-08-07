from enum import Enum

class ScopeEnforcementMode(str, Enum):
    ALL = "ALL"
    ANY = "ANY"
    DISABLED = "DISABLED"

    def __str__(self) -> str:
        return str(self.value)
