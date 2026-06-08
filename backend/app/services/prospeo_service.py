"""
Prospeo API integration for decision maker discovery.
"""

import logging
import asyncio
from typing import List

from app.config.settings import settings
from app.models.pipeline import Contact, SimilarCompany
from app.utils.http_client import make_request

logger = logging.getLogger(__name__)

TARGET_TITLES = [
    "founder", "co-founder", "ceo", "chief executive",
    "cto", "chief technology",
    "vp engineering", "vp of engineering", "vice president engineering",
    "vp product", "vp of product",
    "head of engineering", "head of technology",
]


def _is_target_title(title: str) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(t in title_lower for t in TARGET_TITLES)


async def find_decision_makers(companies: List[SimilarCompany]) -> List[Contact]:
    """
    Use Prospeo API to find decision makers at each company.
    Falls back to mock data if API key not configured.
    """
    if not settings.PROSPEO_API_KEY:
        logger.warning("PROSPEO_API_KEY not set. Using mock data.")
        return _mock_contacts(companies)

    all_contacts: List[Contact] = []
    seen_linkedin = set()

    tasks = [_fetch_contacts_for_domain(company) for company in companies]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error fetching contacts for {companies[i].domain}: {result}")
            continue
        for contact in result:
            if contact.linkedin_url and contact.linkedin_url in seen_linkedin:
                continue
            if contact.linkedin_url:
                seen_linkedin.add(contact.linkedin_url)
            all_contacts.append(contact)

    logger.info(f"Found {len(all_contacts)} decision makers across {len(companies)} companies")
    return all_contacts


async def _fetch_contacts_for_domain(company: SimilarCompany) -> List[Contact]:
    headers = {
        "X-KEY": settings.PROSPEO_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "company_domain": company.domain,
        "limit": settings.MAX_CONTACTS_PER_COMPANY,
        "titles": ["CEO", "CTO", "Founder", "VP Engineering", "VP Product", "Head of Engineering"],
    }

    data = await make_request(
        method="POST",
        url=f"{settings.PROSPEO_API_URL}/domain-search",
        headers=headers,
        json=payload,
    )

    if not data:
        return []

    contacts = []
    items = data.get("response", data.get("data", data.get("leads", [])))

    for item in items:
        title = item.get("job_title", item.get("title", ""))
        if not _is_target_title(title):
            continue

        contact = Contact(
            name=item.get("full_name", item.get("name", "")),
            job_title=title,
            company=company.name or company.domain,
            domain=company.domain,
            linkedin_url=item.get("linkedin_url", item.get("linkedin", "")),
        )
        if contact.name:
            contacts.append(contact)

    return contacts[:settings.MAX_CONTACTS_PER_COMPANY]


def _mock_contacts(companies: List[SimilarCompany]) -> List[Contact]:
    titles = ["CEO", "CTO", "VP Engineering", "Founder", "Head of Engineering"]
    contacts = []
    for i, company in enumerate(companies[:10]):
        title = titles[i % len(titles)]
        contacts.append(Contact(
            name=f"Alex Johnson {i+1}",
            job_title=title,
            company=company.name or company.domain,
            domain=company.domain,
            linkedin_url=f"https://linkedin.com/in/alexjohnson{i+1}",
        ))
    return contacts
