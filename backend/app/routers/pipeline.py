"""Pipeline dashboard data routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Activity, Client, PipelineStage
from app.schemas import ActivityFeedItem, ClientOut, PipelineSummary
from app.services import mock_services

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

STAGE_LABELS = {
    PipelineStage.LEAD: "Lead",
    PipelineStage.INTRO_BOOKED: "Intro Booked",
    PipelineStage.INTRO_COMPLETED: "Intro Completed",
    PipelineStage.DOCUMENTS_REQUESTED: "Docs Requested",
    PipelineStage.DOCUMENTS_RECEIVED: "Docs Received",
    PipelineStage.ENGAGEMENT_LETTER_SENT: "Letter Sent",
    PipelineStage.ENGAGEMENT_SIGNED: "Signed",
    PipelineStage.IN_PROGRESS: "In Progress",
    PipelineStage.REVIEW: "Review",
    PipelineStage.RETURN_COMPLETED: "Return Done",
    PipelineStage.RETURN_SIGNED: "Return Signed",
    PipelineStage.FILED: "Filed",
    PipelineStage.COMPLETED: "Completed",
}


@router.get("/summary", response_model=list[PipelineSummary])
async def get_pipeline_summary(db: AsyncSession = Depends(get_db)):
    summaries = []
    for stage in PipelineStage:
        result = await db.execute(
            select(Client).where(Client.stage == stage).order_by(Client.updated_at.desc())
        )
        clients = result.scalars().all()
        summaries.append(PipelineSummary(
            stage=stage,
            label=STAGE_LABELS.get(stage, stage.value),
            count=len(clients),
            clients=[ClientOut.model_validate(c) for c in clients],
        ))
    return summaries


@router.get("/stats")
async def get_pipeline_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(Client.id)))
    total = total_result.scalar() or 0

    stage_counts = {}
    for stage in PipelineStage:
        result = await db.execute(
            select(func.count(Client.id)).where(Client.stage == stage)
        )
        stage_counts[stage.value] = result.scalar() or 0

    return {
        "total_clients": total,
        "stage_counts": stage_counts,
        "emails_sent": len(mock_services.get_sent_emails()),
        "signature_requests": len(mock_services.get_signature_requests()),
    }


@router.get("/activity-feed", response_model=list[ActivityFeedItem])
async def get_activity_feed(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Activity).order_by(Activity.created_at.desc()).limit(limit)
    )
    activities = result.scalars().all()

    feed = []
    for a in activities:
        client_result = await db.execute(
            select(Client.name).where(Client.id == a.client_id)
        )
        client_name = client_result.scalar() or "Unknown"
        feed.append(ActivityFeedItem(
            id=a.id,
            client_id=a.client_id,
            client_name=client_name,
            action=a.action,
            details=a.details,
            devin_session_id=a.devin_session_id,
            created_at=a.created_at.isoformat(),
        ))
    return feed


@router.get("/emails")
async def get_email_log():
    return mock_services.get_sent_emails()


@router.get("/signatures")
async def get_signature_log():
    return mock_services.get_signature_requests()
