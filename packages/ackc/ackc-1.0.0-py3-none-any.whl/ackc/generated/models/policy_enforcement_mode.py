from enum import Enum

class PolicyEnforcementMode(str, Enum):
    DISABLED = "DISABLED"
    ENFORCING = "ENFORCING"
    PERMISSIVE = "PERMISSIVE"

    def __str__(self) -> str:
        return str(self.value)
