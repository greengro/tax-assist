"""Webhook handlers — Calendly, meeting notes, engagement letter triggers."""

import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Activity, Client, ClientType, DocumentChecklist, PipelineStage
from app.schemas import MeetingNotesPayload
from app.services import devin_api
from app.services import gmail, google_docs, google_drive, google_sheets
from app.services import mock_services

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

APP_URL = os.getenv("APP_URL", "http://localhost:5173")

DEFAULT_CHECKLIST = [
    "W-2 Forms",
    "1099 Forms (Freelance/Investments)",
    "Prior Year Tax Return",
    "Property Tax Statements",
    "Mortgage Interest (Form 1098)",
    "Charitable Donation Receipts",
    "Business Expense Receipts",
    "Health Insurance (Form 1095)",
]


@router.post("/calendly")
async def handle_calendly_webhook(payload: dict, db: AsyncSession = Depends(get_db)):
    """Process Calendly booking → create client, folder, welcome email, Devin session."""
    invitee = payload.get("payload", payload)
    name = invitee.get("name", invitee.get("invitee_name", "Unknown"))
    email = invitee.get("email", invitee.get("invitee_email", ""))
    meeting_time_str = invitee.get("scheduled_time", invitee.get("event_start_time", ""))

    if not email:
        raise HTTPException(status_code=400, detail="Missing email in webhook payload")

    meeting_time = None
    if meeting_time_str:
        try:
            meeting_time = datetime.fromisoformat(meeting_time_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    result = await db.execute(select(Client).where(Client.email == email))
    client = result.scalar_one_or_none()

    if client:
        client.stage = PipelineStage.INTRO_BOOKED
        client.meeting_time = meeting_time
        detail = "Meeting rebooked via Calendly"
    else:
        client = Client(
            name=name, email=email,
            stage=PipelineStage.INTRO_BOOKED,
            meeting_time=meeting_time,
        )
        db.add(client)
        detail = "New client from Calendly booking"
        await db.flush()
        # Create default checklist
        for doc_name in DEFAULT_CHECKLIST:
            db.add(DocumentChecklist(client_id=client.id, doc_name=doc_name))

    await db.flush()

    # Create folder (real Google Drive or mock fallback)
    folder = await google_drive.create_client_folder(name)
    client.folder_url = folder["url"]

    db.add(Activity(client_id=client.id, action="Calendly booking received", details=detail))

    # Send welcome email (real Gmail or mock fallback)
    welcome_subject = "Welcome to Green Grove Tax Services - Your Upcoming Consultation"
    await gmail.send_email(
        to=email,
        subject=welcome_subject,
        body=f"Hi {name},\n\nThank you for booking a consultation! "
        f"Your meeting is scheduled for {meeting_time_str or 'soon'}.\n\n"
        "Please prepare: W-2s, 1099s, prior year returns.\n\n"
        "Best regards,\nGreen Grove Tax Services",
    )
    db.add(Activity(
        client_id=client.id,
        action="Welcome email sent",
        details=f"To: {email} | Subject: {welcome_subject}",
    ))

    # Trigger Devin onboarding session
    devin_result = await devin_api.create_session(
        devin_api.prompt_onboarding(name, email, meeting_time_str or "TBD")
    )
    db.add(Activity(
        client_id=client.id,
        action="Devin onboarding session triggered",
        details=f"Session: {devin_result['session_id']}",
        devin_session_id=devin_result["session_id"],
    ))

    await db.commit()
    await db.refresh(client)

    # Sync to Google Sheets CRM
    try:
        await google_sheets.upsert_client(client)
    except Exception:
        logger.warning("Failed to sync client %s to Google Sheets", client.id, exc_info=True)

    return {
        "status": "processed",
        "client_id": client.id,
        "stage": client.stage.value,
        "devin_session_id": devin_result["session_id"],
        "folder_url": folder["url"],
    }


@router.post("/meeting-notes")
async def handle_meeting_notes(
    payload: MeetingNotesPayload, db: AsyncSession = Depends(get_db),
):
    """Process AI notetaker output → summarize, update CRM, send follow-up, request docs."""
    result = await db.execute(select(Client).where(Client.email == payload.client_email))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail=f"Client not found: {payload.client_email}")

    client.stage = PipelineStage.INTRO_COMPLETED
    client.client_type = ClientType.CUSTOMER
    client.meeting_summary = payload.transcript[:1000]
    if payload.scope_of_services:
        client.scope_of_services = payload.scope_of_services
    if payload.fee_estimate:
        client.fee_estimate = payload.fee_estimate

    db.add(Activity(
        client_id=client.id,
        action="Meeting completed - notes received",
        details=f"Transcript: {len(payload.transcript)} chars, "
        f"Action items: {len(payload.action_items)}",
    ))

    portal_url = f"{APP_URL}/portal/{client.id}"

    # Trigger Devin for post-meeting processing
    devin_result = await devin_api.create_session(
        devin_api.prompt_post_meeting(
            name=client.name, email=client.email,
            transcript=payload.transcript, portal_url=portal_url,
            scope=payload.scope_of_services, fee=payload.fee_estimate,
        )
    )
    db.add(Activity(
        client_id=client.id,
        action="Devin post-meeting session triggered",
        details=f"Session: {devin_result['session_id']}",
        devin_session_id=devin_result["session_id"],
    ))

    # Send follow-up email (real Gmail or mock fallback)
    followup_subject = "Next Steps - Green Grove Tax Services"
    await gmail.send_email(
        to=client.email,
        subject=followup_subject,
        body=f"Hi {client.name},\n\nThank you for meeting with us!\n\n"
        f"Please upload your documents through our secure portal:\n{portal_url}\n\n"
        "Required: W-2s, 1099s, prior year return, property tax statements.\n\n"
        "Best regards,\nGreen Grove Tax Services",
    )
    db.add(Activity(
        client_id=client.id,
        action="Follow-up email sent",
        details=f"To: {client.email} | Subject: {followup_subject}",
    ))

    client.stage = PipelineStage.DOCUMENTS_REQUESTED

    await db.commit()
    await db.refresh(client)

    # Sync to Google Sheets CRM
    try:
        await google_sheets.upsert_client(client)
    except Exception:
        logger.warning("Failed to sync client %s to Google Sheets", client.id, exc_info=True)

    return {
        "status": "processed",
        "client_id": client.id,
        "stage": client.stage.value,
        "devin_session_id": devin_result["session_id"],
        "portal_url": portal_url,
    }


@router.post("/trigger-engagement-letter/{client_id}")
async def trigger_engagement_letter(
    client_id: int,
    services: str = "Individual Tax Return Preparation",
    db: AsyncSession = Depends(get_db),
):
    """Trigger engagement letter + SOW + invoice generation via Devin."""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    devin_result = await devin_api.create_session(
        devin_api.prompt_engagement_letter(client.name, client.email, services)
    )

    client.stage = PipelineStage.ENGAGEMENT_LETTER_SENT
    client.scope_of_services = services

    # Extract folder ID from folder_url for placing docs in client folder
    folder_id = None
    if client.folder_url and "folders/" in client.folder_url:
        folder_id = client.folder_url.rsplit("folders/", 1)[-1]

    # 1-3. Create real Google Docs (engagement letter + SOW + invoice)
    letter_result = await google_docs.create_engagement_letter(
        client_name=client.name, client_email=client.email,
        services=services, fee_estimate=client.fee_estimate,
        folder_id=folder_id,
    )
    sow_result = await google_docs.create_statement_of_work(
        client_name=client.name, client_email=client.email,
        services=services, fee_estimate=client.fee_estimate,
        folder_id=folder_id,
    )
    invoice_result = await google_docs.create_invoice(
        client_name=client.name, client_email=client.email,
        services=services, fee_estimate=client.fee_estimate,
        folder_id=folder_id,
    )

    db.add(Activity(
        client_id=client.id,
        action="Engagement letter & SOW & Invoice created in Google Docs",
        details=(
            f"Services: {services}. "
            f"Letter: {letter_result['doc_url']}. "
            f"SOW: {sow_result['doc_url']}. "
            f"Invoice: {invoice_result['doc_url']}. "
            f"Devin session: {devin_result['session_id']}"
        ),
        devin_session_id=devin_result["session_id"],
    ))

    # 4. Documents are uploaded to client's Drive folder via folder_id above

    # 5. Send Engagement Letter and SOW via DocuSign for e-signature
    letter_sig = await mock_services.send_for_signature(
        client_name=client.name, client_email=client.email,
        document_name="Engagement Letter",
    )
    sow_sig = await mock_services.send_for_signature(
        client_name=client.name, client_email=client.email,
        document_name="Statement of Work",
    )
    db.add(Activity(
        client_id=client.id,
        action="Engagement letter & SOW sent via DocuSign",
        details=(
            f"To: {client.email} | "
            f"Letter envelope: {letter_sig.envelope_id} | "
            f"SOW envelope: {sow_sig.envelope_id}"
        ),
    ))

    # 6. Send email notification about pending signature
    eng_subject = "Action Required: Please Sign Your Engagement Documents - Green Grove Tax Services"
    await gmail.send_email(
        to=client.email,
        subject=eng_subject,
        body=f"Hi {client.name},\n\n"
        f"Your engagement documents are ready for review and signature.\n\n"
        f"We have sent the following documents via DocuSign:\n"
        f"1. Engagement Letter (Envelope: {letter_sig.envelope_id})\n"
        f"2. Statement of Work (Envelope: {sow_sig.envelope_id})\n\n"
        f"You can also view the documents directly:\n"
        f"- Engagement Letter: {letter_result['doc_url']}\n"
        f"- Statement of Work: {sow_result['doc_url']}\n"
        f"- Invoice: {invoice_result['doc_url']}\n\n"
        f"Services: {services}\n\n"
        f"Please check your email for the DocuSign signing request and "
        f"complete your signature at your earliest convenience.\n\n"
        f"Best regards,\nGreen Grove Tax Services",
    )
    db.add(Activity(
        client_id=client.id,
        action="Engagement letter email sent",
        details=f"To: {client.email} | Subject: {eng_subject}",
    ))

    # 7. CRM stage already set to ENGAGEMENT_LETTER_SENT above

    await db.commit()
    await db.refresh(client)

    # Sync to Google Sheets CRM
    try:
        await google_sheets.upsert_client(client)
    except Exception:
        logger.warning("Failed to sync client %s to Google Sheets", client.id, exc_info=True)

    return {
        "status": "processed",
        "client_id": client.id,
        "stage": client.stage.value,
        "devin_session_id": devin_result["session_id"],
        "documents": {
            "engagement_letter": letter_result["doc_url"],
            "statement_of_work": sow_result["doc_url"],
            "invoice": invoice_result["doc_url"],
        },
        "docusign": {
            "engagement_letter_envelope": letter_sig.envelope_id,
            "sow_envelope": sow_sig.envelope_id,
        },
    }


@router.post("/check-documents/{client_id}")
async def check_documents(client_id: int, db: AsyncSession = Depends(get_db)):
    """Check document checklist and send follow-up for missing items via Devin."""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    missing = [item.doc_name for item in client.checklist_items if item.required and not item.received]
    portal_url = f"{APP_URL}/portal/{client.id}"

    if missing:
        devin_result = await devin_api.create_session(
            devin_api.prompt_document_check(client.name, client.email, missing, portal_url)
        )
        db.add(Activity(
            client_id=client.id,
            action="Document follow-up triggered",
            details=f"Missing: {', '.join(missing)}. Devin session: {devin_result['session_id']}",
            devin_session_id=devin_result["session_id"],
        ))
        reminder_subject = "Reminder: Missing Documents - Green Grove Tax Services"
        await gmail.send_email(
            to=client.email,
            subject=reminder_subject,
            body=f"Hi {client.name},\n\nWe still need: {', '.join(missing)}.\n\n"
            f"Upload at: {portal_url}\n\nBest regards,\nGreen Grove Tax Services",
        )
        db.add(Activity(
            client_id=client.id,
            action="Document reminder email sent",
            details=f"To: {client.email} | Subject: {reminder_subject}",
        ))
        await db.commit()
        return {"status": "follow_up_sent", "missing_documents": missing,
                "devin_session_id": devin_result["session_id"]}
    else:
        client.stage = PipelineStage.DOCUMENTS_RECEIVED
        db.add(Activity(
            client_id=client.id,
            action="All documents received",
            details="Document checklist complete",
        ))
        await db.commit()
        return {"status": "all_received", "missing_documents": []}


@router.post("/trigger-analysis/{client_id}")
async def trigger_return_analysis(client_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger AI analysis of completed return: owed/refund, next year planning."""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    devin_result = await devin_api.create_session(
        devin_api.prompt_return_analysis(client.name, client.email)
    )

    db.add(Activity(
        client_id=client.id,
        action="Return analysis triggered",
        details=f"Devin session: {devin_result['session_id']}",
        devin_session_id=devin_result["session_id"],
    ))
    await db.commit()

    return {
        "status": "analysis_triggered",
        "devin_session_id": devin_result["session_id"],
    }
