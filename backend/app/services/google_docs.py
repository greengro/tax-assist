"""Google Docs API integration — engagement letter and SOW generation.

Creates real Google Docs in the client's Drive folder using OAuth2 user
credentials (the same refresh token used for Gmail).  This avoids the
service-account 0-byte Drive storage quota limitation.

Falls back to mock when credentials are not configured.

Required env vars (shared with Gmail):
  GMAIL_CLIENT_ID      – OAuth2 client ID
  GMAIL_CLIENT_SECRET  – OAuth2 client secret
  GMAIL_REFRESH_TOKEN  – OAuth2 refresh token (must include docs + drive scopes)

Optional:
  GOOGLE_DRIVE_FOLDER_ID – parent folder where client folders live
"""

import logging
import os
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
DOCS_URL = "https://docs.googleapis.com/v1/documents"
DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"


def _is_configured() -> bool:
    return bool(
        os.getenv("GMAIL_CLIENT_ID", "")
        and os.getenv("GMAIL_CLIENT_SECRET", "")
        and os.getenv("GMAIL_REFRESH_TOKEN", "")
    )


def _format_fee(fee_estimate: str | float | None) -> str:
    """Format fee_estimate for display, handling str, float, or None."""
    if fee_estimate is None or fee_estimate == "":
        return "To be determined"
    if isinstance(fee_estimate, (int, float)):
        return f"${fee_estimate:,.2f}"
    # Already a string — prefix with $ if not already present
    return fee_estimate if fee_estimate.startswith("$") else f"${fee_estimate}"


async def _get_access_token() -> str:
    """Exchange the refresh token for a short-lived access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "client_id": os.getenv("GMAIL_CLIENT_ID", ""),
            "client_secret": os.getenv("GMAIL_CLIENT_SECRET", ""),
            "refresh_token": os.getenv("GMAIL_REFRESH_TOKEN", ""),
            "grant_type": "refresh_token",
        })
        resp.raise_for_status()
        return resp.json()["access_token"]


async def _create_doc(title: str, headers: dict) -> dict:
    """Create a blank Google Doc and return its metadata."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DOCS_URL,
            headers=headers,
            json={"title": title},
        )
        resp.raise_for_status()
        return resp.json()


async def _batch_update_doc(
    doc_id: str, requests: list, headers: dict,
) -> None:
    """Insert content into a Google Doc via batchUpdate."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DOCS_URL}/{doc_id}:batchUpdate",
            headers=headers,
            json={"requests": requests},
        )
        resp.raise_for_status()


async def _move_doc_to_folder(
    doc_id: str, folder_id: str, headers: dict,
) -> None:
    """Move a document into the specified Drive folder."""
    async with httpx.AsyncClient() as client:
        # Get current parents
        resp = await client.get(
            f"{DRIVE_FILES_URL}/{doc_id}",
            headers=headers,
            params={"fields": "parents"},
        )
        resp.raise_for_status()
        prev_parents = ",".join(resp.json().get("parents", []))

        # Move to target folder
        resp = await client.patch(
            f"{DRIVE_FILES_URL}/{doc_id}",
            headers=headers,
            params={
                "addParents": folder_id,
                "removeParents": prev_parents,
                "fields": "id,parents",
            },
        )
        resp.raise_for_status()


async def create_engagement_letter(
    client_name: str,
    client_email: str,
    services: str,
    fee_estimate: str | float | None = None,
    folder_id: str | None = None,
) -> dict:
    """Create an Engagement Letter as a Google Doc in the client's folder.

    Returns dict with 'doc_id', 'doc_url', and 'title'.
    """
    if not _is_configured():
        mock_id = f"mock-doc-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info("[MOCK DOCS] Engagement letter for %s", client_name)
        return {
            "doc_id": mock_id,
            "doc_url": f"https://docs.google.com/document/d/{mock_id}/edit",
            "title": f"Engagement Letter - {client_name}",
            "mock": True,
        }

    try:
        access_token = await _get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        today = datetime.now().strftime("%B %d, %Y")
        title = f"Engagement Letter - {client_name}"
        fee_line = _format_fee(fee_estimate)

        # 1. Create blank doc
        doc = await _create_doc(title, headers)
        doc_id = doc["documentId"]

        # 2. Insert content via batchUpdate
        content = _build_engagement_letter_content(
            client_name, client_email, services, fee_line, today,
        )
        await _batch_update_doc(doc_id, content, headers)

        # 3. Move doc into client folder (if provided)
        if folder_id:
            try:
                await _move_doc_to_folder(doc_id, folder_id, headers)
            except Exception:
                logger.warning(
                    "Could not move doc %s into folder %s", doc_id, folder_id,
                )

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        logger.info("[GOOGLE DOCS] Created engagement letter: %s", doc_url)

        return {
            "doc_id": doc_id, "doc_url": doc_url,
            "title": title, "mock": False,
        }
    except Exception:
        logger.exception(
            "Failed to create engagement letter for %s", client_name,
        )
        mock_id = f"mock-doc-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "doc_id": mock_id,
            "doc_url": f"https://docs.google.com/document/d/{mock_id}/edit",
            "title": f"Engagement Letter - {client_name}",
            "mock": True,
        }


async def create_statement_of_work(
    client_name: str,
    client_email: str,
    services: str,
    fee_estimate: str | float | None = None,
    folder_id: str | None = None,
) -> dict:
    """Create a Statement of Work as a Google Doc in the client's folder."""
    if not _is_configured():
        mock_id = f"mock-sow-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info("[MOCK DOCS] SOW for %s", client_name)
        return {
            "doc_id": mock_id,
            "doc_url": f"https://docs.google.com/document/d/{mock_id}/edit",
            "title": f"Statement of Work - {client_name}",
            "mock": True,
        }

    try:
        access_token = await _get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        today = datetime.now().strftime("%B %d, %Y")
        title = f"Statement of Work - {client_name}"
        fee_line = _format_fee(fee_estimate)

        doc = await _create_doc(title, headers)
        doc_id = doc["documentId"]

        content = _build_sow_content(client_name, services, fee_line, today)
        await _batch_update_doc(doc_id, content, headers)

        if folder_id:
            try:
                await _move_doc_to_folder(doc_id, folder_id, headers)
            except Exception:
                logger.warning(
                    "Could not move SOW %s into folder %s", doc_id, folder_id,
                )

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        logger.info("[GOOGLE DOCS] Created SOW: %s", doc_url)

        return {
            "doc_id": doc_id, "doc_url": doc_url,
            "title": title, "mock": False,
        }
    except Exception:
        logger.exception("Failed to create SOW for %s", client_name)
        mock_id = f"mock-sow-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "doc_id": mock_id,
            "doc_url": f"https://docs.google.com/document/d/{mock_id}/edit",
            "title": f"Statement of Work - {client_name}",
            "mock": True,
        }


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
