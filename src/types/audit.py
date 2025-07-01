from enum import Enum
from dataclasses import dataclass
from typing import Literal, List
from pydantic import BaseModel, Field
from .jobs import Job, VisaSponsor, JobStatus, RoleType, EducationLevel


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
    is_product_job: bool = Field(description="Whether the job is a product-focused role like 'Product Manager' or 'Associate Product Manager'. This excludes engineering roles and will mostly be true for positions that have 'Product' in the title or are directly related to product management.")
    is_consulting_job: bool = Field(description="Whether the job is a consulting-focused role like 'Consultant' or 'Associate Consultant'. This excludes engineering roles and will mostly be true for positions that have 'Consulting' in the title or are directly related to consulting.")
    is_engineering_job: bool = Field(description="Whether the job is an engineering-focused role like 'Software Engineer' or 'Data Scientist'. This excludes product and consulting roles and will mostly be true for positions that have 'Engineering' in the title or are directly related to engineering.")
    is_other_job: bool = Field(description="Whether the job is not a product, consulting, or engineering role. This is a catch-all for jobs that don't fit into the other categories.")
    min_education_level: EducationLevel = Field(description="Minimum education level required for the job, inferred from the job description. This should be a string like 'bachelors' or 'masters'.")
    min_years_experience: int = Field(description="Minimum years of experience required for the job, inferred from the job description. This must be a number.")

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



    
    
