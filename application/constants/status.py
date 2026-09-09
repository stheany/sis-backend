# application/constants/status.py
from enum import Enum

class Status(Enum):
    PENDING = 1
    SUCCESS = 2
    FAIL = 3
    ERROR = 4
    COMMITTED = 5
    REJECTED = 6
    STATELESS_VALIDATION_FAILED = 7

    def __int__(self):
        """Return integer ID (STATUS_ID)"""
        return self.value

    @classmethod
    def from_name(cls, name: str):
        """Get enum member by status name (case-insensitive)."""
        return cls[name.upper()]

    @classmethod
    def choices(cls):
        """Return dict mapping of name → id."""
        return {member.name: member.value for member in cls}

    def __str__(self):
        """Readable label."""
        return self.name