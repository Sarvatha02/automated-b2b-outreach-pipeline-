"""
Pydantic models for the Outreach Pipeline.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class PipelineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


# --- Request Models ---

class PipelineStartRequest(BaseModel):
    domain: str = Field(..., example="openai.com", description="Target company domain")


class ApprovalRequest(BaseModel):
    pipeline_id: str
    approved: bool


# --- Data Models ---

class SimilarCompany(BaseModel):
    domain: str
    name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    description: Optional[str] = None


class Contact(BaseModel):
    name: str
    job_title: str
    company: str
    domain: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool = False


class EmailLog(BaseModel):
    id: str
    contact: Contact
    subject: str
    body: str
    status: EmailStatus = EmailStatus.PENDING
    sent_at: Optional[datetime] = None
    error: Optional[str] = None
    retries: int = 0


# --- Stage Models ---

class StageInfo(BaseModel):
    name: str
    status: StageStatus = StageStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    message: str = ""
    progress: int = 0  # 0-100
    count: int = 0
    error: Optional[str] = None


# --- Pipeline Session ---

class PipelineSession(BaseModel):
    id: str
    domain: str
    status: PipelineStatus = PipelineStatus.IDLE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    stages: dict = Field(default_factory=lambda: {
        "discovery": StageInfo(name="Similar Company Discovery"),
        "contacts": StageInfo(name="Decision Maker Discovery"),
        "emails": StageInfo(name="Email Resolution"),
        "outreach": StageInfo(name="Outreach Generation"),
        "sending": StageInfo(name="Email Sending"),
    })

    similar_companies: List[SimilarCompany] = []
    contacts: List[Contact] = []
    email_logs: List[EmailLog] = []

    # Summary
    total_companies: int = 0
    total_contacts: int = 0
    total_emails_found: int = 0
    total_sent: int = 0
    total_failed: int = 0


# --- Response Models ---

class PipelineResponse(BaseModel):
    pipeline_id: str
    status: PipelineStatus
    message: str


class PipelineSummary(BaseModel):
    pipeline_id: str
    domain: str
    status: PipelineStatus
    total_companies: int
    total_contacts: int
    total_emails_found: int
    total_sent: int
    total_failed: int
    stages: dict
    sample_contacts: List[Contact] = []


class EmailLogsResponse(BaseModel):
    pipeline_id: str
    total: int
    sent: int
    failed: int
    pending: int
    logs: List[EmailLog]
