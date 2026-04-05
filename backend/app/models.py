"""SQLAlchemy models matching the full engagement workflow."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PipelineStage(str, enum.Enum):
    LEAD = "lead"
    INTRO_BOOKED = "intro_booked"
    INTRO_COMPLETED = "intro_completed"
    DOCUMENTS_REQUESTED = "documents_requested"
    DOCUMENTS_RECEIVED = "documents_received"
    ENGAGEMENT_LETTER_SENT = "engagement_letter_sent"
    ENGAGEMENT_SIGNED = "engagement_signed"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    RETURN_COMPLETED = "return_completed"
    RETURN_SIGNED = "return_signed"
    FILED = "filed"
    COMPLETED = "completed"


class ClientType(str, enum.Enum):
    PROSPECT = "prospect"
    CUSTOMER = "customer"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client_type: Mapped[ClientType] = mapped_column(
        Enum(ClientType), default=ClientType.PROSPECT
    )
    stage: Mapped[PipelineStage] = mapped_column(
        Enum(PipelineStage), default=PipelineStage.LEAD
    )
    # CRM fields from workflow diagram
    scope_of_services: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fee_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    referral_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    needs_extension: Mapped[bool | None] = mapped_column(default=None)
    # Meeting and notes
    meeting_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    meeting_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # File management
    folder_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    activities: Mapped[list["Activity"]] = relationship(
        back_populates="client", lazy="selectin", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="client", lazy="selectin", cascade="all, delete-orphan"
    )
    checklist_items: Mapped[list["DocumentChecklist"]] = relationship(
        back_populates="client", lazy="selectin", cascade="all, delete-orphan"
    )


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    action: Mapped[str] = mapped_column(String(255))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    devin_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="activities")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    filename: Mapped[str] = mapped_column(String(500))
    doc_type: Mapped[str] = mapped_column(String(100))
    file_path: Mapped[str] = mapped_column(String(1000))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="documents")


class DocumentChecklist(Base):
    """Tracks which required documents have been received per client."""

    __tablename__ = "document_checklist"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    doc_name: Mapped[str] = mapped_column(String(255))
    required: Mapped[bool] = mapped_column(default=True)
    received: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="checklist_items")
