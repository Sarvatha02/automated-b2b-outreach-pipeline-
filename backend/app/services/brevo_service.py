"""
Brevo (Sendinblue) API integration for sending outreach emails.
"""

import asyncio
import logging
from typing import List

from app.config.settings import settings
from app.models.pipeline import EmailLog, EmailStatus
from app.utils.http_client import make_request

logger = logging.getLogger(__name__)


async def send_emails(logs: List[EmailLog]) -> List[EmailLog]:
    """
    Send all pending emails via Brevo. Retry transient failures.
    Continues processing even if individual emails fail.
    """
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not set. Simulating sends.")
        return _mock_send(logs)

    tasks = [_send_single(log) for log in logs if log.status == EmailStatus.PENDING]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            pending_logs = [l for l in logs if l.status == EmailStatus.PENDING]
            if i < len(pending_logs):
                pending_logs[i].status = EmailStatus.FAILED
                pending_logs[i].error = str(result)

    return logs


async def _send_single(log: EmailLog) -> EmailLog:
    from datetime import datetime

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": log.contact.email, "name": log.contact.name}],
        "subject": log.subject,
        "textContent": log.body,
        "htmlContent": _text_to_html(log.body),
    }

    log.status = EmailStatus.RETRYING

    for attempt in range(settings.MAX_RETRIES):
        data = await make_request(
            method="POST",
            url=f"{settings.BREVO_API_URL}/smtp/email",
            headers=headers,
            json=payload,
        )

        if data and data.get("messageId"):
            log.status = EmailStatus.SENT
            log.sent_at = datetime.utcnow()
            logger.info(f"Email sent to {log.contact.email}")
            return log

        log.retries += 1
        if attempt < settings.MAX_RETRIES - 1:
            await asyncio.sleep(settings.RETRY_DELAY * (2 ** attempt))

    log.status = EmailStatus.FAILED
    log.error = "Failed after max retries"
    logger.error(f"Email failed for {log.contact.email}")
    return log


def _text_to_html(text: str) -> str:
    """Convert plain text email to basic HTML."""
    lines = text.split("\n")
    html_lines = []
    for line in lines:
        if line.strip():
            html_lines.append(f"<p>{line}</p>")
        else:
            html_lines.append("<br>")
    return f"<html><body>{''.join(html_lines)}</body></html>"


def _mock_send(logs: List[EmailLog]) -> List[EmailLog]:
    """Simulate sending for demo without API key."""
    from datetime import datetime
    import random

    for log in logs:
        if log.status == EmailStatus.PENDING:
            # Simulate 90% success rate
            if random.random() < 0.9:
                log.status = EmailStatus.SENT
                log.sent_at = datetime.utcnow()
            else:
                log.status = EmailStatus.FAILED
                log.error = "Simulated failure"
    return logs
