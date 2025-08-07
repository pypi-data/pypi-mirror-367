from enum import Enum

class UnmanagedAttributePolicy(str, Enum):
    ADMIN_EDIT = "ADMIN_EDIT"
    ADMIN_VIEW = "ADMIN_VIEW"
    ENABLED = "ENABLED"

    def __str__(self) -> str:
        return str(self.value)
