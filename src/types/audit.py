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


class SiteType(str, Enum):
    """Type of job posting site."""
    APM = "apm"
    CONSULTING = "consulting"
    OTHER = "other"


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
    title: str = Field(description="Title of the job position")
    location: str = Field(description="Geographic location of the job")
    description: str = Field(description="Detailed description of the job requirements and responsibilities")
    other: str = Field(description="Additional information or notes about the job posting")
    jobType: RoleType = Field(description="Type of job (internship or full-time)")
    salaryText: str = Field(description="Salary of the job, e.g. $100 - $130k")
    visaSponsored: VisaSponsor = Field(description="Whether the job is visa sponsored")
    status: JobStatus = Field(description="Status of the job")
    site: SiteType = Field(
        description="Type of job posting site. Must be one of: 'apm' for Product-related jobs, 'consulting' for Consulting-related jobs, or 'other' for other types of jobs"
    )

@dataclass
class OpenRoleAuditTask:
    id: int
    url: str
    status: AuditStatus
    status_message: str
    updated_at: str
    created_at: str
    site: str
    company: str
    job_title: str
    role_type: str



    
    
