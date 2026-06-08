"""
Ocean.io API integration for similar company discovery.
"""

import logging
from typing import List

from app.config.settings import settings
from app.models.pipeline import SimilarCompany
from app.utils.http_client import make_request

logger = logging.getLogger(__name__)

TARGET_TITLES = [
    "Founder", "Co-Founder", "CEO", "Chief Executive Officer",
    "CTO", "Chief Technology Officer",
    "VP Engineering", "VP of Engineering", "Vice President Engineering",
    "VP Product", "VP of Product",
    "Head of Engineering", "Head of Technology",
]


async def discover_similar_companies(domain: str, max_results: int = None) -> List[SimilarCompany]:
    """
    Call Ocean.io API to find companies similar to the given domain.
    Falls back to mock data if API key is not configured.
    """
    limit = max_results or settings.MAX_SIMILAR_COMPANIES

    if not settings.OCEAN_API_KEY:
        logger.warning("OCEAN_API_KEY not set. Using mock data.")
        return _mock_similar_companies(domain, limit)

    headers = {
        "Authorization": f"Bearer {settings.OCEAN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "domain": domain,
        "limit": limit,
    }

    all_companies: List[SimilarCompany] = []
    page = 1

    while len(all_companies) < limit:
        payload["page"] = page
        logger.info(f"Fetching similar companies page {page} for {domain}")

        data = await make_request(
            method="POST",
            url=f"{settings.OCEAN_API_URL}/similar-companies",
            headers=headers,
            json=payload,
        )

        if not data:
            logger.error(f"Failed to fetch similar companies for {domain}")
            break

        items = data.get("companies", data.get("data", []))
        if not items:
            break

        for item in items:
            company = SimilarCompany(
                domain=item.get("domain", ""),
                name=item.get("name", item.get("company_name", "")),
                industry=item.get("industry", ""),
                employee_count=item.get("employee_count", item.get("employees", None)),
                description=item.get("description", ""),
            )
            if company.domain:
                all_companies.append(company)

        # Deduplication
        seen = set()
        unique = []
        for c in all_companies:
            if c.domain not in seen:
                seen.add(c.domain)
                unique.append(c)
        all_companies = unique

        # Pagination
        has_more = data.get("has_more", data.get("hasMore", False))
        if not has_more or len(all_companies) >= limit:
            break
        page += 1

    logger.info(f"Discovered {len(all_companies)} similar companies for {domain}")
    return all_companies[:limit]


def _mock_similar_companies(domain: str, limit: int) -> List[SimilarCompany]:
    """Mock data for development/testing without API keys."""
    real_domains = [
        ("stripe.com", "Stripe", "Financial Services"),
        ("twilio.com", "Twilio", "Telecommunications"),
        ("plaid.com", "Plaid", "Financial Services"),
        ("auth0.com", "Auth0", "Computer Security"),
        ("sendgrid.com", "SendGrid", "Internet"),
        ("algolia.com", "Algolia", "Internet"),
        ("vercel.com", "Vercel", "Internet"),
        ("supabase.com", "Supabase", "Computer Software"),
        ("render.com", "Render", "Computer Software"),
        ("netlify.com", "Netlify", "Internet")
    ]
    
    mock = []
    for i in range(min(limit, len(real_domains))):
        d, name, ind = real_domains[i]
        mock.append(SimilarCompany(
            domain=d,
            name=name,
            industry=ind,
            employee_count=500 + i * 100,
            description=f"Popular tech company like {domain}"
        ))
        
    return mock
