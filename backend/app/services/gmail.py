"""Gmail SMTP email service.

Sends real emails via Gmail SMTP using an App Password.
Falls back to mock logging when credentials are not configured.

Required env vars:
  GMAIL_ADDRESS   – the Gmail address to send from (e.g. carson@yunafi.com)
  GMAIL_APP_PASSWORD – a 16-char App Password generated at
      https://myaccount.google.com/apppasswords
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _is_configured() -> bool:
    return bool(os.getenv("GMAIL_ADDRESS", "") and os.getenv("GMAIL_APP_PASSWORD", ""))


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
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())
        logger.info("[GMAIL] Sent email to %s | Subject: %s", to, subject)
        return {"status": "sent", "to": to, "subject": subject}
    except Exception:
        logger.exception("[GMAIL] Failed to send email to %s", to)
        # Fall back to mock so the workflow doesn't break
        logger.info("[MOCK EMAIL FALLBACK] To: %s | Subject: %s", to, subject)
        return {"status": "mock_fallback", "to": to, "subject": subject}
