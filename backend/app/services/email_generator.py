"""
Personalized outreach email generation.
"""

import logging
from typing import Tuple
from app.models.pipeline import Contact

logger = logging.getLogger(__name__)

TEMPLATES = {
    "CEO": {
        "subject": "Partnership opportunity with {company}",
        "body": """Hi {first_name},

I came across {company} and was genuinely impressed by what you're building. As {title} you clearly have a strong vision for where the company is headed.

I'm reaching out because I believe there's a meaningful opportunity for collaboration that could accelerate {company}'s growth trajectory.

We work with companies like yours to [specific value proposition]. Our approach has helped similar teams achieve measurable results in a short timeframe.

Would you be open to a 20-minute call this week to explore if there's a fit? I'll keep it focused and respect your time.

Best regards,
{sender_name}
{sender_title}"""
    },
    "CTO": {
        "subject": "Technical collaboration for {company}",
        "body": """Hi {first_name},

I've been following {company}'s engineering work and it's clear you're tackling some interesting technical challenges.

As {title} at {company}, I imagine you're constantly evaluating tools and partnerships that could strengthen your engineering org.

I'd love to share how we've helped other engineering teams [specific benefit] — from reducing toil to accelerating delivery cycles.

Would you have 20 minutes this week to connect? Happy to adjust to your schedule.

Best,
{sender_name}
{sender_title}"""
    },
    "Founder": {
        "subject": "Quick question about {company}'s growth plans",
        "body": """Hi {first_name},

Building {company} from the ground up takes a rare combination of vision and execution — and from what I can see, you've got both.

I'm reaching out founders who are scaling rapidly and who value leveraging the right partnerships at the right time.

We've helped several startups in your space [specific outcome] — and I think there could be a strong fit here.

Worth a quick 20-minute call to explore? I'll make it worth your time.

Warm regards,
{sender_name}
{sender_title}"""
    },
    "VP Engineering": {
        "subject": "Engineering efficiency at {company}",
        "body": """Hi {first_name},

As {title} at {company}, I imagine you're always looking for ways to help your team ship faster and with higher quality.

I'm reaching out because we work specifically with engineering leaders to [specific benefit] — without adding process overhead.

Happy to share a few concrete examples of what we've done for similar teams. Would you be open to a brief call this week?

Best,
{sender_name}
{sender_title}"""
    },
    "VP Product": {
        "subject": "Product velocity at {company}",
        "body": """Hi {first_name},

Congrats on what you're building at {company} — it's clear the product is gaining real traction.

As {title}, I know you're juggling roadmap priorities, stakeholder alignment, and getting insights to your team fast.

We help product leaders at companies like {company} [specific outcome]. The impact is usually measurable within the first quarter.

Would you be open to a 20-minute exploratory call? I'd love to share what's been working for others in your space.

Best regards,
{sender_name}
{sender_title}"""
    },
    "default": {
        "subject": "Collaboration opportunity with {company}",
        "body": """Hi {first_name},

I came across {company} and was excited by the work you're doing. As {title}, I imagine you're always looking for ways to push things forward.

I'd love to share how we've helped similar companies [specific benefit] — and explore whether there's a good fit.

Would you be open to a 20-minute call this week?

Best,
{sender_name}
{sender_title}"""
    }
}

SENDER_NAME = "Alex Rivera"
SENDER_TITLE = "Head of Partnerships"


def generate_email(contact: Contact) -> Tuple[str, str]:
    """Generate personalized subject and body for a contact."""
    first_name = contact.name.split()[0] if contact.name else "there"
    company = contact.company or contact.domain
    title = contact.job_title or "Leader"

    # Pick template based on title
    template_key = "default"
    title_lower = title.lower()
    if "ceo" in title_lower or "chief executive" in title_lower:
        template_key = "CEO"
    elif "cto" in title_lower or "chief technology" in title_lower:
        template_key = "CTO"
    elif "founder" in title_lower:
        template_key = "Founder"
    elif "vp" in title_lower and "engineering" in title_lower:
        template_key = "VP Engineering"
    elif "vp" in title_lower and "product" in title_lower:
        template_key = "VP Product"

    template = TEMPLATES[template_key]
    vars = {
        "first_name": first_name,
        "company": company,
        "title": title,
        "sender_name": SENDER_NAME,
        "sender_title": SENDER_TITLE,
    }

    subject = template["subject"].format(**vars)
    body = template["body"].format(**vars)

    return subject, body
