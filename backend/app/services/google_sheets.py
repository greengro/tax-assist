"""Google Sheets CRM integration — sync client data to a shared spreadsheet."""

import json
import logging
import os
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADERS = [
    "ID", "Name", "Email", "Phone", "Company", "State",
    "Client Type", "Stage", "Scope of Services", "Fee Estimate",
    "Referral Source", "Owner", "Needs Extension",
    "Meeting Time", "Meeting Summary", "Folder URL",
    "Created At", "Updated At",
]


def _get_sheets_service():
    key_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "")
    if not key_json:
        return None
    creds = service_account.Credentials.from_service_account_info(
        json.loads(key_json), scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def _fmt(val) -> str:
    """Format a value for the spreadsheet."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, datetime):
        return val.isoformat()
    return str(val)


async def ensure_headers() -> bool:
    """Write header row if row 1 is empty. Returns True if headers were written."""
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    service = _get_sheets_service()
    if not service or not spreadsheet_id:
        logger.warning("[GOOGLE SHEETS] Credentials or sheet ID not set — skipping")
        return False

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range="Sheet1!A1:R1"
    ).execute()
    existing = result.get("values", [])
    if existing and existing[0]:
        return False

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A1:R1",
        valueInputOption="RAW",
        body={"values": [HEADERS]},
    ).execute()
    logger.info("[GOOGLE SHEETS] Header row written")
    return True


async def upsert_client(client) -> bool:
    """Add or update a client row in the CRM spreadsheet.

    Searches for existing row by client ID. If found, updates it; otherwise appends.
    """
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    service = _get_sheets_service()
    if not service or not spreadsheet_id:
        logger.warning("[GOOGLE SHEETS] Credentials or sheet ID not set — skipping sync")
        return False

    row = [
        _fmt(client.id),
        _fmt(client.name),
        _fmt(client.email),
        _fmt(client.phone),
        _fmt(client.company),
        _fmt(client.state),
        _fmt(client.client_type.value if client.client_type else None),
        _fmt(client.stage.value if client.stage else None),
        _fmt(client.scope_of_services),
        _fmt(client.fee_estimate),
        _fmt(client.referral_source),
        _fmt(client.owner),
        _fmt(client.needs_extension),
        _fmt(client.meeting_time),
        _fmt(client.meeting_summary[:200] if client.meeting_summary else None),
        _fmt(client.folder_url),
        _fmt(client.created_at),
        _fmt(client.updated_at),
    ]

    # Find existing row by ID
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range="Sheet1!A:A"
    ).execute()
    ids = result.get("values", [])

    row_index = None
    client_id_str = str(client.id)
    for i, id_row in enumerate(ids):
        if i == 0:
            continue  # skip header
        if id_row and id_row[0] == client_id_str:
            row_index = i + 1  # 1-indexed
            break

    if row_index:
        # Update existing row
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"Sheet1!A{row_index}:R{row_index}",
            valueInputOption="RAW",
            body={"values": [row]},
        ).execute()
        logger.info("[GOOGLE SHEETS] Updated client %s at row %d", client.name, row_index)
    else:
        # Append new row
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A:R",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute()
        logger.info("[GOOGLE SHEETS] Added client %s to CRM", client.name)

    return True
