"""Google Drive integration — create client folders in a shared parent folder."""

import json
import logging
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]


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
    parent_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    service = _get_drive_service()
    if not service or not parent_folder_id:
        logger.warning("[GOOGLE DRIVE] Credentials or folder ID not set — using mock")
        slug = client_name.lower().replace(" ", "-")
        return {"name": client_name, "url": f"https://drive.google.com/drive/folders/mock-{slug}"}

    file_metadata = {
        "name": client_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }
    folder = service.files().create(body=file_metadata, fields="id, webViewLink").execute()
    folder_url = folder.get("webViewLink", f"https://drive.google.com/drive/folders/{folder['id']}")

    logger.info("[GOOGLE DRIVE] Created folder '%s' → %s", client_name, folder_url)
    return {"name": client_name, "url": folder_url}
