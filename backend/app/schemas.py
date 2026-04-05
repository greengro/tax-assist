"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel

from app.models import ClientType, PipelineStage


# --- Client ---

class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    company: str | None = None
    state: str | None = None
    referral_source: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    state: str | None = None
    stage: PipelineStage | None = None
    client_type: ClientType | None = None
    scope_of_services: str | None = None
    fee_estimate: float | None = None
    referral_source: str | None = None
    owner: str | None = None
    needs_extension: bool | None = None
    notes: str | None = None
    meeting_summary: str | None = None


class ActivityOut(BaseModel):
    id: int
    action: str
    details: str | None
    devin_session_id: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: int
    filename: str
    doc_type: str
    uploaded_at: datetime
    model_config = {"from_attributes": True}


class ChecklistItemOut(BaseModel):
    id: int
    doc_name: str
    required: bool
    received: bool
    model_config = {"from_attributes": True}


class ClientOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    company: str | None
    state: str | None
    client_type: ClientType
    stage: PipelineStage
    scope_of_services: str | None
    fee_estimate: float | None
    referral_source: str | None
    owner: str | None
    needs_extension: bool | None
    meeting_time: datetime | None
    meeting_summary: str | None
    notes: str | None
    folder_url: str | None
    created_at: datetime
    updated_at: datetime
    activities: list[ActivityOut] = []
    documents: list[DocumentOut] = []
    checklist_items: list[ChecklistItemOut] = []
    model_config = {"from_attributes": True}


# --- Pipeline ---

class PipelineSummary(BaseModel):
    stage: PipelineStage
    label: str
    count: int
    clients: list[ClientOut]


# --- Webhooks ---

class MeetingNotesPayload(BaseModel):
    client_email: str
    transcript: str
    action_items: list[str] = []
    scope_of_services: str | None = None
    fee_estimate: float | None = None


# --- Activity Feed ---

class ActivityFeedItem(BaseModel):
    id: int
    client_id: int
    client_name: str
    action: str
    details: str | None
    devin_session_id: str | None
    created_at: str
