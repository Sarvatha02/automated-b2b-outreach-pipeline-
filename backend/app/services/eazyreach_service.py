"""
Eazyreach API integration for email resolution from LinkedIn URLs.
"""

import logging
import asyncio
from typing import List

from app.config.settings import settings
from app.models.pipeline import Contact
from app.utils.http_client import make_request

logger = logging.getLogger(__name__)


async def resolve_emails(contacts: List[Contact]) -> List[Contact]:
    """
    Use Eazyreach API to find verified work emails from LinkedIn URLs.
    Skips contacts without LinkedIn URLs. Continues on failures.
    """
    if not settings.EAZYREACH_API_KEY:
        logger.warning("EAZYREACH_API_KEY not set. Using mock data.")
        return _mock_emails(contacts)

    tasks = []
    for contact in contacts:
        if contact.linkedin_url:
            tasks.append(_resolve_single_email(contact))
        else:
            tasks.append(_passthrough(contact))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    resolved = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"Email resolution failed for {contacts[i].name}: {result}")
            resolved.append(contacts[i])  # keep without email, continue
        else:
            resolved.append(result)

    found = sum(1 for c in resolved if c.email)
    logger.info(f"Resolved {found}/{len(contacts)} emails")
    return resolved


async def _resolve_single_email(contact: Contact) -> Contact:
    headers = {
        "Authorization": f"Bearer {settings.EAZYREACH_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"linkedin_url": contact.linkedin_url}

    data = await make_request(
        method="POST",
        url=f"{settings.EAZYREACH_API_URL}/find-email",
        headers=headers,
        json=payload,
    )

    if not data:
        return contact

    email = data.get("email", data.get("work_email", ""))
    verified = data.get("verified", data.get("email_verified", False))

    if email and "@" in email:
        contact.email = email
        contact.email_verified = bool(verified)

    return contact


async def _passthrough(contact: Contact) -> Contact:
    return contact


def _mock_emails(contacts: List[Contact]) -> List[Contact]:
    """Generate mock emails for testing."""
    for i, contact in enumerate(contacts):
        first_name = contact.name.split()[0].lower() if contact.name else "contact"
        domain = contact.domain or "company.com"
        contact.email = f"{first_name}@{domain}"
        contact.email_verified = True
    return contacts
