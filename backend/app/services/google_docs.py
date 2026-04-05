"""Google Docs API integration — engagement letter and SOW generation.

Creates real Google Docs in the client's Drive folder using a service account.
Falls back to mock when credentials are not configured.

Required env vars:
  GOOGLE_SERVICE_ACCOUNT_KEY – JSON key for the service account
  GOOGLE_DRIVE_FOLDER_ID     – parent folder where client folders live
"""

import json
import logging
import os
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


def _get_services() -> tuple | None:
    """Return (docs_service, drive_service) or None if not configured."""
    key_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "")
    if not key_json:
        return None
    try:
        creds = Credentials.from_service_account_info(
            json.loads(key_json), scopes=SCOPES,
        )
        docs = build("docs", "v1", credentials=creds, cache_discovery=False)
        drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        return docs, drive
    except Exception:
        logger.exception("Failed to build Google Docs/Drive services")
        return None


def _is_configured() -> bool:
    return bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", ""))


async def create_engagement_letter(
    client_name: str,
    client_email: str,
    services: str,
    fee_estimate: float | None = None,
    folder_id: str | None = None,
) -> dict:
    """Create an Engagement Letter as a Google Doc in the client's folder.

    Returns dict with 'doc_id', 'doc_url', and 'title'.
    """
    result = _get_services()
    if not result:
        mock_id = f"mock-doc-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info("[MOCK DOCS] Engagement letter for %s", client_name)
        return {
            "doc_id": mock_id,
            "doc_url": f"https://docs.google.com/document/d/{mock_id}/edit",
            "title": f"Engagement Letter - {client_name}",
            "mock": True,
        }

    docs_service, drive_service = result
    today = datetime.now().strftime("%B %d, %Y")
    title = f"Engagement Letter - {client_name}"
    fee_line = f"${fee_estimate:,.2f}" if fee_estimate else "To be determined"

    # 1. Create blank doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # 2. Insert content via batchUpdate
    content = _build_engagement_letter_content(
        client_name, client_email, services, fee_line, today,
    )
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": content},
    ).execute()

    # 3. Move doc into client folder (if provided)
    if folder_id:
        try:
            # Get current parents and move
            file_meta = drive_service.files().get(
                fileId=doc_id, fields="parents",
            ).execute()
            prev_parents = ",".join(file_meta.get("parents", []))
            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=prev_parents,
                fields="id, parents",
            ).execute()
        except Exception:
            logger.warning("Could not move doc %s into folder %s", doc_id, folder_id)

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    logger.info("[GOOGLE DOCS] Created engagement letter: %s", doc_url)

    return {"doc_id": doc_id, "doc_url": doc_url, "title": title, "mock": False}


async def create_statement_of_work(
    client_name: str,
    client_email: str,
    services: str,
    fee_estimate: float | None = None,
    folder_id: str | None = None,
) -> dict:
    """Create a Statement of Work as a Google Doc in the client's folder."""
    result = _get_services()
    if not result:
        mock_id = f"mock-sow-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info("[MOCK DOCS] SOW for %s", client_name)
        return {
            "doc_id": mock_id,
            "doc_url": f"https://docs.google.com/document/d/{mock_id}/edit",
            "title": f"Statement of Work - {client_name}",
            "mock": True,
        }

    docs_service, drive_service = result
    today = datetime.now().strftime("%B %d, %Y")
    title = f"Statement of Work - {client_name}"
    fee_line = f"${fee_estimate:,.2f}" if fee_estimate else "To be determined"

    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    content = _build_sow_content(client_name, services, fee_line, today)
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": content},
    ).execute()

    if folder_id:
        try:
            file_meta = drive_service.files().get(
                fileId=doc_id, fields="parents",
            ).execute()
            prev_parents = ",".join(file_meta.get("parents", []))
            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=prev_parents,
                fields="id, parents",
            ).execute()
        except Exception:
            logger.warning("Could not move SOW %s into folder %s", doc_id, folder_id)

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    logger.info("[GOOGLE DOCS] Created SOW: %s", doc_url)

    return {"doc_id": doc_id, "doc_url": doc_url, "title": title, "mock": False}


# ---------------------------------------------------------------------------
# Document content builders (Google Docs batchUpdate requests)
# ---------------------------------------------------------------------------

def _build_engagement_letter_content(
    client_name: str, client_email: str, services: str,
    fee_line: str, date: str,
) -> list[dict]:
    """Build a list of Google Docs API insertText requests for the letter."""
    # Content is inserted in REVERSE order because each insert pushes
    # previous content down.  We build the list top-to-bottom then reverse.
    lines = [
        "ENGAGEMENT LETTER\n",
        "Green Grove Tax Services\n",
        f"Date: {date}\n\n",
        f"To: {client_name}\n",
        f"Email: {client_email}\n\n",
        f"Dear {client_name},\n\n",
        "Thank you for choosing Green Grove Tax Services. This letter confirms "
        "our engagement to provide the following services:\n\n",
        f"Services: {services}\n\n",
        f"Fee: {fee_line}\n\n",
        "Scope of Engagement:\n",
        "We will prepare your tax returns based on the information you provide. "
        "We will not audit or verify the data you submit, although we may ask "
        "for clarification or additional documentation.\n\n",
        "Client Responsibilities:\n",
        "You are responsible for providing all necessary information and documents "
        "in a timely manner. This includes W-2s, 1099s, prior year returns, and "
        "any other relevant financial documents.\n\n",
        "Confidentiality:\n",
        "All information you provide will be kept strictly confidential and used "
        "solely for the purpose of preparing your tax returns.\n\n",
        "Please indicate your acceptance by replying to this email or signing below.\n\n",
        "Sincerely,\n",
        "Green Grove Tax Services\n",
        "carson@yunafi.com\n",
    ]

    full_text = "".join(lines)
    requests = [{"insertText": {"location": {"index": 1}, "text": full_text}}]

    # Bold the title
    title_end = len("ENGAGEMENT LETTER\n") + 1
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": 1, "endIndex": title_end},
            "textStyle": {"bold": True, "fontSize": {"magnitude": 18, "unit": "PT"}},
            "fields": "bold,fontSize",
        }
    })

    return requests


def _build_sow_content(
    client_name: str, services: str, fee_line: str, date: str,
) -> list[dict]:
    """Build Google Docs API requests for the Statement of Work."""
    lines = [
        "STATEMENT OF WORK\n",
        "Green Grove Tax Services\n",
        f"Date: {date}\n\n",
        f"Client: {client_name}\n\n",
        "1. Services to be Provided\n",
        f"   {services}\n\n",
        "2. Fee Schedule\n",
        f"   Total Fee: {fee_line}\n",
        "   Payment Terms: Due upon completion of services\n\n",
        "3. Timeline\n",
        "   - Document collection: Within 2 weeks of engagement\n",
        "   - Tax preparation: Within 5 business days of receiving all documents\n",
        "   - Review and filing: Within 3 business days of preparation\n\n",
        "4. Deliverables\n",
        "   - Completed federal tax return\n",
        "   - Completed state tax return (if applicable)\n",
        "   - Tax planning memo with recommendations for next year\n",
        "   - Year-over-year comparison summary\n\n",
        "5. Assumptions\n",
        "   - Client provides all necessary documents in a timely manner\n",
        "   - No significant changes to tax law during engagement period\n",
        "   - Standard individual or business return (complex situations may incur additional fees)\n\n",
    ]

    full_text = "".join(lines)
    requests = [{"insertText": {"location": {"index": 1}, "text": full_text}}]

    title_end = len("STATEMENT OF WORK\n") + 1
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": 1, "endIndex": title_end},
            "textStyle": {"bold": True, "fontSize": {"magnitude": 18, "unit": "PT"}},
            "fields": "bold,fontSize",
        }
    })

    return requests
