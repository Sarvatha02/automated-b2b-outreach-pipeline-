"""
Pipeline orchestrator - coordinates all pipeline stages.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

from app.config.settings import settings
from app.config.store import store
from app.models.pipeline import (
    PipelineSession, PipelineStatus, StageStatus, StageInfo,
    EmailLog, EmailStatus
)
from app.services.ocean_service import discover_similar_companies
from app.services.prospeo_service import find_decision_makers
from app.services.eazyreach_service import resolve_emails
from app.services.email_generator import generate_email
from app.services.brevo_service import send_emails

logger = logging.getLogger(__name__)


def create_pipeline(domain: str) -> PipelineSession:
    """Create a new pipeline session."""
    session = PipelineSession(
        id=str(uuid.uuid4()),
        domain=domain.strip().lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").split("/")[0],
    )
    store.save(session)
    return session


async def run_pipeline(pipeline_id: str) -> None:
    """
    Run the full pipeline asynchronously.
    Updates session state at each stage.
    """
    session = store.get(pipeline_id)
    if not session:
        logger.error(f"Pipeline {pipeline_id} not found")
        return

    session.status = PipelineStatus.RUNNING
    store.save(session)

    try:
        # Stage 1: Similar Company Discovery
        await _run_stage(session, "discovery", _stage_discovery)

        # Stage 2: Decision Maker Discovery
        await _run_stage(session, "contacts", _stage_contacts)

        # Stage 3: Email Resolution
        await _run_stage(session, "emails", _stage_emails)

        # Stage 4: Outreach Email Generation
        await _run_stage(session, "outreach", _stage_outreach)

        # Update summary counts
        session.total_companies = len(session.similar_companies)
        session.total_contacts = len(session.contacts)
        session.total_emails_found = sum(1 for c in session.contacts if c.email)

        session.status = PipelineStatus.AWAITING_APPROVAL
        store.save(session)
        logger.info(f"Pipeline {pipeline_id} ready for approval: {session.total_companies} companies, {session.total_contacts} contacts, {session.total_emails_found} emails")

    except Exception as e:
        logger.error(f"Pipeline {pipeline_id} failed: {e}", exc_info=True)
        session.status = PipelineStatus.FAILED
        store.save(session)


async def _run_stage(session: PipelineSession, stage_key: str, stage_fn) -> None:
    stage = session.stages[stage_key]
    stage.status = StageStatus.RUNNING
    stage.started_at = datetime.utcnow()
    stage.progress = 0
    store.save(session)

    try:
        await stage_fn(session, stage)
        stage.status = StageStatus.COMPLETED
        stage.progress = 100
        stage.completed_at = datetime.utcnow()
    except Exception as e:
        stage.status = StageStatus.FAILED
        stage.error = str(e)
        stage.completed_at = datetime.utcnow()
        logger.error(f"Stage {stage_key} failed: {e}", exc_info=True)
        raise

    store.save(session)


async def _stage_discovery(session: PipelineSession, stage: StageInfo) -> None:
    stage.message = f"Searching for companies similar to {session.domain}..."
    store.save(session)

    companies = await discover_similar_companies(session.domain, settings.MAX_SIMILAR_COMPANIES)
    session.similar_companies = companies
    stage.count = len(companies)
    stage.message = f"Found {len(companies)} similar companies"
    stage.progress = 100


async def _stage_contacts(session: PipelineSession, stage: StageInfo) -> None:
    stage.message = "Discovering decision makers..."
    store.save(session)

    contacts = await find_decision_makers(session.similar_companies)
    session.contacts = contacts
    stage.count = len(contacts)
    stage.message = f"Found {len(contacts)} decision makers"
    stage.progress = 100


async def _stage_emails(session: PipelineSession, stage: StageInfo) -> None:
    stage.message = "Resolving work emails..."
    store.save(session)

    contacts_with_linkedin = [c for c in session.contacts if c.linkedin_url]
    stage.message = f"Resolving emails for {len(contacts_with_linkedin)} contacts..."
    store.save(session)

    resolved = await resolve_emails(session.contacts)
    session.contacts = resolved
    found = sum(1 for c in resolved if c.email)
    stage.count = found
    stage.message = f"Resolved {found} verified emails"
    stage.progress = 100


async def _stage_outreach(session: PipelineSession, stage: StageInfo) -> None:
    stage.message = "Generating personalized outreach emails..."
    store.save(session)

    logs = []
    contacts_with_email = [c for c in session.contacts if c.email]

    for contact in contacts_with_email:
        subject, body = generate_email(contact)
        log = EmailLog(
            id=str(uuid.uuid4()),
            contact=contact,
            subject=subject,
            body=body,
            status=EmailStatus.PENDING,
        )
        logs.append(log)

    session.email_logs = logs
    stage.count = len(logs)
    stage.message = f"Generated {len(logs)} personalized emails"
    stage.progress = 100


async def execute_sending(pipeline_id: str) -> None:
    """Send emails after user approval."""
    session = store.get(pipeline_id)
    if not session:
        return

    session.status = PipelineStatus.SENDING
    session.stages["sending"].status = StageStatus.RUNNING
    session.stages["sending"].started_at = datetime.utcnow()
    session.stages["sending"].message = "Sending emails..."
    store.save(session)

    try:
        updated_logs = await send_emails(session.email_logs)
        session.email_logs = updated_logs

        session.total_sent = sum(1 for l in updated_logs if l.status == EmailStatus.SENT)
        session.total_failed = sum(1 for l in updated_logs if l.status == EmailStatus.FAILED)

        session.stages["sending"].status = StageStatus.COMPLETED
        session.stages["sending"].completed_at = datetime.utcnow()
        session.stages["sending"].count = session.total_sent
        session.stages["sending"].message = f"Sent {session.total_sent}, Failed {session.total_failed}"
        session.status = PipelineStatus.COMPLETED

    except Exception as e:
        session.stages["sending"].status = StageStatus.FAILED
        session.stages["sending"].error = str(e)
        session.status = PipelineStatus.FAILED

    store.save(session)
