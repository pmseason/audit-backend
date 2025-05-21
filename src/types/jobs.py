from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Literal, Union
from datetime import datetime


class Industry(str, Enum):
    TECH = "tech"
    NON_TECH = "nonTech"


class RoleType(str, Enum):
    FULL_TIME = "full-time"
    INTERNSHIP = "internship"


class VisaSponsor(str, Enum):
    YES = "yes"
    NO = "no"
    UNSURE = "unsure"


class JobStatus(str, Enum):
    OPEN = "open"
    POSTPONED = "postponed"
    NOT_OPEN = "notOpen"
    CLOSED = "closed"
    CANCELLED = "cancelled"


@dataclass
class Logo:
    id: str
    filename_disk: str
    url: str


@dataclass
class Company:
    id: str
    name: str
    type: Industry
    created_at: datetime
    location: str
    logo: Optional[Logo] = None


@dataclass
class Job:
    id: str
    company: Company
    job_type: RoleType
    status: JobStatus
    title: str
    season: str
    url: str
    description: Optional[str] = None
    hidden: bool = False
    created_at: str = ""
    date_added: str = ""
    salary_text: str = ""
    visa_sponsored: VisaSponsor = VisaSponsor.UNSURE


@dataclass
class JobFilter:
    status: Optional[Union[Literal["all"], JobStatus]] = None
    job_type: Optional[Union[Literal["all"], RoleType]] = None
    company_type: Optional[Union[Literal["all"], Industry]] = None
