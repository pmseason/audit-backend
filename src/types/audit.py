from enum import Enum
from dataclasses import dataclass
from typing import Literal, List
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


@dataclass
class ScrapedJob:
    id: int
    title: str
    company: str
    location: str
    description: str
    task: int
    url: str
    other: str 
    

@dataclass
class OpenRoleAuditTask:
    id: int
    url: str
    extra_notes: str
    status: AuditStatus
    status_message: str
    scraped_jobs: List[ScrapedJob]
    updated_at: str
    created_at: str



    
    
