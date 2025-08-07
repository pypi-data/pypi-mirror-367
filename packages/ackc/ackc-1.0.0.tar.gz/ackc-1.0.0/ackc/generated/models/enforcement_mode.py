from enum import Enum

class EnforcementMode(str, Enum):
    DISABLED = "DISABLED"
    ENFORCING = "ENFORCING"
    PERMISSIVE = "PERMISSIVE"

    def __str__(self) -> str:
        return str(self.value)
