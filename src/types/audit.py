from enum import Enum
from dataclasses import dataclass
from typing import Literal, List
from pydantic import BaseModel, Field
from .jobs import Job, VisaSponsor, JobStatus, RoleType


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
    job_type: str
    salary: str
    visa_sponsored: str
    status: str
    
class ScrapedJobAgent(BaseModel):
    """Model representing a scraped job posting with its details."""
    id: int = Field(description="Unique identifier for the scraped job")
    title: str = Field(description="Title of the job position")
    company: str = Field(description="Name of the company offering the position")
    location: str = Field(description="Geographic location of the job")
    description: str = Field(description="Detailed description of the job requirements and responsibilities")
    task: int = Field(description="ID of the associated task")
    url: str = Field(description="URL of the job posting")
    other: str = Field(description="Additional information or notes about the job posting")
    job_type: RoleType = Field(description="Type of job (internship or full-time)")
    salary: str = Field(description="Salary of the job")
    visa_sponsored: VisaSponsor = Field(description="Whether the job is visa sponsored")
    status: JobStatus = Field(description="Status of the job")

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



    
    
