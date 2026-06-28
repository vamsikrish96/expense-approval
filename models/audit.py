from enum import Enum
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuditAction(str, Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RESUBMITTED = "RESUBMITTED"
    PROCESSED = "PROCESSED"
    DELETED = "DELETED"


class AuditLog(BaseModel):
    id: UUID
    expense_id: UUID
    action: AuditAction
    actor_id: str
    timestamp: datetime
    previous_state: Optional[dict[str, Any]] = None
    new_state: Optional[dict[str, Any]] = None
    reason: Optional[str] = None

    class Config:
        use_enum_values = False
