"""Devin API integration service.

Triggers autonomous Devin sessions for multi-step automation tasks.
Falls back to mock mode when API credentials are not configured.
"""

import logging
import os
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

DEVIN_API_KEY = os.getenv("DEVIN_API_KEY", "")
DEVIN_ORG_ID = os.getenv("DEVIN_ORG_ID", "")
DEVIN_API_BASE = "https://api.devin.ai/v3"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {DEVIN_API_KEY}",
        "Content-Type": "application/json",
    }


def _is_configured() -> bool:
    return bool(DEVIN_API_KEY and DEVIN_ORG_ID)


async def create_session(prompt: str, playbook_id: str | None = None) -> dict:
    """Create a new Devin session. Returns mock response if not configured."""
    if not _is_configured():
        mock_id = f"mock-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info("[MOCK DEVIN] Session created: %s | Prompt: %s", mock_id, prompt[:120])
        return {
            "session_id": mock_id,
            "status": "running",
            "url": f"https://app.devin.ai/sessions/{mock_id}",
            "mock": True,
        }

    body: dict = {"prompt": prompt}
    if playbook_id:
        body["playbook_id"] = playbook_id

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{DEVIN_API_BASE}/organizations/{DEVIN_ORG_ID}/sessions",
            headers=_headers(),
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "session_id": data.get("session_id", ""),
            "status": data.get("status", "running"),
            "url": data.get("url"),
            "mock": False,
        }


async def get_session_status(session_id: str) -> dict:
    if not _is_configured() or session_id.startswith("mock-"):
        return {"session_id": session_id, "status": "completed", "mock": True}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{DEVIN_API_BASE}/organizations/{DEVIN_ORG_ID}/sessions/{session_id}",
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


# --- Pre-built prompt templates ---

def prompt_onboarding(name: str, email: str, meeting_time: str) -> str:
    return f"""New client onboarding for Green Grove Tax Services:

Client: {name} ({email})
Meeting: {meeting_time}

Steps:
1. Create a client folder in Google Drive under /Clients/{name}
   - Subfolders: Meeting Notes, Documents, Tax Returns, Correspondence
2. Add client to CRM spreadsheet: Name, Email, Meeting Date, Stage="Intro Booked"
3. Send welcome email to {email}:
   Subject: Welcome to Green Grove Tax Services
   Include: meeting time, list of documents to prepare (W-2s, 1099s, prior returns)
4. Confirm completion.
"""


def prompt_post_meeting(
    name: str, email: str, transcript: str, portal_url: str,
    scope: str | None = None, fee: float | None = None,
) -> str:
    scope_line = f"\nScope of Services: {scope}" if scope else ""
    fee_line = f"\nFee Estimate: ${fee:,.2f}" if fee else ""
    return f"""Post-meeting processing for Green Grove Tax Services:

Client: {name} ({email}){scope_line}{fee_line}

Meeting Transcript:
{transcript[:2000]}

Steps:
1. Summarize transcript into key points and action items
2. Update CRM with: meeting summary, expected services, fee estimate, scope, prospect/customer status
3. Pull prior year fields and meeting notes; prompt accountant for changes
4. Save summary to client's Google Drive folder
5. Send follow-up email to {email} with:
   - Link to meeting notes
   - Secure portal link for document uploads: {portal_url}
   - List of required documents (W-2s, 1099s, prior returns, property tax statements)
6. Update CRM stage to "Documents Requested"
7. Confirm completion.
"""


def prompt_engagement_letter(name: str, email: str, services: str) -> str:
    return f"""Generate engagement documents for Green Grove Tax Services:

Client: {name} ({email})
Services: {services}

Steps:
1. Generate Engagement Letter from template with client info and services
2. Generate Statement of Work with scope and standard pricing
3. Generate Invoice with client name and services
4. Upload all documents to client's Google Drive folder
5. Send Engagement Letter and SOW via DocuSign to {email} for e-signature
6. Send email notification about pending signature
7. Update CRM stage to "Engagement Letter Sent"
8. Confirm completion.
"""


def prompt_document_check(name: str, email: str, missing_docs: list[str], portal_url: str) -> str:
    docs_list = "\n".join(f"  - {d}" for d in missing_docs)
    return f"""Document follow-up for Green Grove Tax Services:

Client: {name} ({email})

Missing documents:
{docs_list}

Steps:
1. Send follow-up email to {email} requesting the missing documents listed above
2. Include the portal upload link: {portal_url}
3. Update CRM notes with "Follow-up sent for missing documents on [today's date]"
4. Confirm completion.
"""


def prompt_return_analysis(name: str, email: str) -> str:
    return f"""Tax return analysis for Green Grove Tax Services:

Client: {name} ({email})

Steps:
1. Analyze the completed tax return for:
   - Amount owed or refund expected
   - Key deductions and credits applied
2. Generate next year tax planning recommendations
3. Create a memo with bulleted notes summarizing:
   - Filing status and key numbers
   - Year-over-year comparison (if prior year available)
   - Recommended actions for next tax year
4. Save analysis to client's folder
5. Send summary email to {email} with key findings
6. Confirm completion.
"""
