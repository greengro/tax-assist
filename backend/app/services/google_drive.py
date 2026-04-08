"""Google Drive integration — create client folders in a shared parent folder."""

import asyncio
import json
import logging
import os
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]

CLIENT_SUBFOLDERS = [
    "Meeting Notes",
    "Documents",
    "Tax Returns",
    "Correspondence",
]


def _get_drive_service():
    key_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "")
    if not key_json:
        return None
    creds = service_account.Credentials.from_service_account_info(
        json.loads(key_json), scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def _create_folder_sync(service, name: str, parent_id: str) -> dict:
    """Create a single folder and return the API response."""
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    return service.files().create(body=metadata, fields="id, webViewLink").execute()


async def create_client_folder(
    client_name: str,
    subfolders: Optional[list[str]] = None,
) -> dict:
    """Create a client folder with standard subfolders inside the shared Clients folder.

    Args:
        client_name: Display name for the client folder.
        subfolders: Override the default subfolder list. Pass an empty list to
                    skip subfolder creation. Defaults to CLIENT_SUBFOLDERS.

    Returns dict with 'name', 'url', and 'subfolders' keys.
    Falls back to mock if credentials not configured.
    """
    if subfolders is None:
        subfolders = CLIENT_SUBFOLDERS

    parent_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    service = _get_drive_service()
    if not service or not parent_folder_id:
        logger.warning("[GOOGLE DRIVE] Credentials or folder ID not set — using mock")
        slug = client_name.lower().replace(" ", "-")
        mock_url = f"https://drive.google.com/drive/folders/mock-{slug}"
        return {
            "name": client_name,
            "url": mock_url,
            "subfolders": {sf: f"{mock_url}/{sf.lower().replace(' ', '-')}" for sf in subfolders},
        }

    try:
        # Create the top-level client folder
        folder = await asyncio.to_thread(
            _create_folder_sync, service, client_name, parent_folder_id,
        )
        folder_id = folder["id"]
        folder_url = folder.get("webViewLink", f"https://drive.google.com/drive/folders/{folder_id}")

        logger.info("[GOOGLE DRIVE] Created folder '%s' → %s", client_name, folder_url)

        # Create subfolders inside the client folder
        created_subfolders: dict[str, str] = {}
        for sf_name in subfolders:
            sf = await asyncio.to_thread(
                _create_folder_sync, service, sf_name, folder_id,
            )
            sf_url = sf.get("webViewLink", f"https://drive.google.com/drive/folders/{sf['id']}")
            created_subfolders[sf_name] = sf_url
            logger.info("[GOOGLE DRIVE]   ↳ Subfolder '%s' → %s", sf_name, sf_url)

        return {"name": client_name, "url": folder_url, "subfolders": created_subfolders}
    except Exception:
        logger.exception("[GOOGLE DRIVE] Failed to create folder for '%s'", client_name)
        slug = client_name.lower().replace(" ", "-")
        mock_url = f"https://drive.google.com/drive/folders/mock-{slug}"
        return {
            "name": client_name,
            "url": mock_url,
            "subfolders": {sf: f"{mock_url}/{sf.lower().replace(' ', '-')}" for sf in subfolders},
        }
