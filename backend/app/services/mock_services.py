"""Mock external services for demo purposes.

In production these would integrate with real APIs:
- Email: SendGrid / AWS SES
- Drive: Google Drive API
- DocuSign: DocuSign eSignature API
- Notetaker: Fireflies / Otter.ai
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


# --- Email Service ---

@dataclass
class EmailRecord:
    to: str
    subject: str
    body: str
    sent_at: datetime = field(default_factory=datetime.now)

_sent_emails: list[EmailRecord] = []


async def send_email(to: str, subject: str, body: str) -> EmailRecord:
    record = EmailRecord(to=to, subject=subject, body=body)
    _sent_emails.append(record)
    logger.info("[MOCK EMAIL] To: %s | Subject: %s", to, subject)
    return record


def get_sent_emails() -> list[dict]:
    return [
        {"to": e.to, "subject": e.subject, "body": e.body, "sent_at": e.sent_at.isoformat()}
        for e in reversed(_sent_emails)
    ]


# --- Google Drive Service ---

@dataclass
class DriveFolder:
    name: str
    url: str
    created_at: datetime = field(default_factory=datetime.now)

_folders: list[DriveFolder] = []


async def create_client_folder(client_name: str) -> DriveFolder:
    slug = client_name.lower().replace(" ", "-")
    folder = DriveFolder(
        name=client_name,
        url=f"https://drive.google.com/drive/folders/mock-{slug}",
    )
    _folders.append(folder)
    logger.info("[MOCK DRIVE] Created folder for %s", client_name)
    return folder


# --- DocuSign Service ---

@dataclass
class SignatureRequest:
    envelope_id: str
    client_name: str
    client_email: str
    document_name: str
    status: str = "sent"
    created_at: datetime = field(default_factory=datetime.now)

_signatures: list[SignatureRequest] = []
_sig_counter = 0


async def send_for_signature(
    client_name: str, client_email: str, document_name: str,
) -> SignatureRequest:
    global _sig_counter
    _sig_counter += 1
    req = SignatureRequest(
        envelope_id=f"env-{_sig_counter:04d}",
        client_name=client_name,
        client_email=client_email,
        document_name=document_name,
    )
    _signatures.append(req)
    logger.info("[MOCK DOCUSIGN] Sent '%s' to %s for signature", document_name, client_email)
    return req


def get_signature_requests() -> list[dict]:
    return [
        {
            "envelope_id": s.envelope_id,
            "client_name": s.client_name,
            "document_name": s.document_name,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
        }
        for s in reversed(_signatures)
    ]
