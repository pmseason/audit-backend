from enum import Enum
from dataclasses import dataclass
from typing import Literal
from .jobs import Job


class AuditStatus(str, Enum):
    NOT_RUN = "not_run"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


@dataclass
class ClosedRoleAuditTask:
    id: str
    job: Job
    url: str
    status: AuditStatus
    status_message: str
    result: Literal["open", "closed", "unsure"]
    justification: str
    screenshot: str 
    
    
