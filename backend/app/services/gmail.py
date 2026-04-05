"""Gmail SMTP email service.

Sends real emails via Gmail SMTP using an App Password.
Falls back to mock logging when credentials are not configured.

Tries SMTP_SSL (port 465) first, then STARTTLS (port 587). Both have a
10-second connection timeout so the workflow never hangs if SMTP ports are
blocked by a firewall.

Required env vars:
  GMAIL_ADDRESS   – the Gmail address to send from (e.g. carson@yunafi.com)
  GMAIL_APP_PASSWORD – a 16-char App Password generated at
      https://myaccount.google.com/apppasswords
"""

import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
CONNECT_TIMEOUT = 10  # seconds


def _is_configured() -> bool:
    return bool(os.getenv("GMAIL_ADDRESS", "") and os.getenv("GMAIL_APP_PASSWORD", ""))


def _send_smtp(sender: str, password: str, to: str, msg: str) -> None:
    """Try SSL (465) then STARTTLS (587). Raises on total failure."""
    # Attempt 1: SMTP_SSL on port 465
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, 465, timeout=CONNECT_TIMEOUT) as server:
            server.login(sender, password)
            server.sendmail(sender, to, msg)
            return
    except Exception:
        logger.debug("[GMAIL] Port 465 failed, trying 587")

    # Attempt 2: STARTTLS on port 587
    with smtplib.SMTP(SMTP_HOST, 587, timeout=CONNECT_TIMEOUT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, to, msg)


async def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email via Gmail SMTP. Falls back to mock if not configured."""
    sender = os.getenv("GMAIL_ADDRESS", "")
    password = os.getenv("GMAIL_APP_PASSWORD", "")

    if not sender or not password:
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
        # Run blocking SMTP in a thread so we don't block the event loop
        await asyncio.to_thread(_send_smtp, sender, password, to, msg.as_string())
        logger.info("[GMAIL] Sent email to %s | Subject: %s", to, subject)
        return {"status": "sent", "to": to, "subject": subject}
    except Exception:
        logger.exception("[GMAIL] Failed to send email to %s", to)
        # Fall back to mock so the workflow doesn't break
        logger.info("[MOCK EMAIL FALLBACK] To: %s | Subject: %s", to, subject)
        return {"status": "mock_fallback", "to": to, "subject": subject}
