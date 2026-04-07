"""Gmail API email service.

Sends real emails via the Gmail API (HTTPS — no SMTP ports needed).
Falls back to mock logging when credentials are not configured.

Uses OAuth2 with a stored refresh token.  One-time setup:
  1. Enable Gmail API in GCP project
  2. Create OAuth2 Desktop client credentials
  3. Run  python scripts/gmail_auth.py  to obtain a refresh token
  4. Set the env vars below

Required env vars:
  GMAIL_ADDRESS          – the Gmail address to send from
  GMAIL_CLIENT_ID        – OAuth2 client ID
  GMAIL_CLIENT_SECRET    – OAuth2 client secret
  GMAIL_REFRESH_TOKEN    – OAuth2 refresh token from the auth script
"""

import base64
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def _is_configured() -> bool:
    return bool(
        os.getenv("GMAIL_ADDRESS", "")
        and os.getenv("GMAIL_CLIENT_ID", "")
        and os.getenv("GMAIL_CLIENT_SECRET", "")
        and os.getenv("GMAIL_REFRESH_TOKEN", "")
    )


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


async def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email via the Gmail API. Falls back to mock if not configured."""
    sender = os.getenv("GMAIL_ADDRESS", "")

    if not _is_configured():
        logger.info("[MOCK EMAIL] To: %s | Subject: %s", to, subject)
        return {"status": "mock", "to": to, "subject": subject}

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Green Grove Tax Services <{sender}>"
    msg["To"] = to
    msg["Subject"] = subject

    # Plain-text body
    msg.attach(MIMEText(body, "plain"))

    # Simple HTML version
    html_body = body.replace("\n", "<br>")
    msg.attach(MIMEText(f"<html><body><p>{html_body}</p></body></html>", "html"))

    try:
        access_token = await _get_access_token()
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                SEND_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                json={"raw": raw},
            )
            resp.raise_for_status()

        logger.info("[GMAIL API] Sent email to %s | Subject: %s", to, subject)
        return {"status": "sent", "to": to, "subject": subject}
    except Exception:
        logger.exception("[GMAIL API] Failed to send email to %s", to)
        # Fall back to mock so the workflow doesn't break
        logger.info("[MOCK EMAIL FALLBACK] To: %s | Subject: %s", to, subject)
        return {"status": "mock_fallback", "to": to, "subject": subject}
