"""Google Drive integration — create client folders in a shared parent folder."""

import json
import logging
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")


def _get_drive_service():
    key_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "")
    if not key_json:
        return None
    creds = service_account.Credentials.from_service_account_info(
        json.loads(key_json), scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


async def create_client_folder(client_name: str) -> dict:
    """Create a subfolder for the client inside the shared Clients folder.

    Returns dict with 'name' and 'url' keys.
    Falls back to mock if credentials not configured.
    """
    service = _get_drive_service()
    if not service or not PARENT_FOLDER_ID:
        logger.warning("[GOOGLE DRIVE] Credentials or folder ID not set — using mock")
        slug = client_name.lower().replace(" ", "-")
        return {"name": client_name, "url": f"https://drive.google.com/drive/folders/mock-{slug}"}

    file_metadata = {
        "name": client_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [PARENT_FOLDER_ID],
    }
    folder = service.files().create(body=file_metadata, fields="id, webViewLink").execute()
    folder_url = folder.get("webViewLink", f"https://drive.google.com/drive/folders/{folder['id']}")

    logger.info("[GOOGLE DRIVE] Created folder '%s' → %s", client_name, folder_url)
    return {"name": client_name, "url": folder_url}
