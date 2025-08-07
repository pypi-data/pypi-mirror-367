from enum import Enum

class MembershipType(str, Enum):
    MANAGED = "MANAGED"
    UNMANAGED = "UNMANAGED"

    def __str__(self) -> str:
        return str(self.value)
