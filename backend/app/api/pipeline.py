"""
Pipeline API endpoints.
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models.pipeline import PipelineStartRequest, PipelineResponse, ApprovalRequest, PipelineSummary
from app.services.pipeline_service import create_pipeline, run_pipeline, execute_sending
from app.config.store import store

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start", response_model=PipelineResponse)
async def start_pipeline(request: PipelineStartRequest, background_tasks: BackgroundTasks):
    """Start a new pipeline for a given company domain."""
    if not request.domain or "." not in request.domain:
        raise HTTPException(status_code=400, detail="Invalid domain. Example: openai.com")

    session = create_pipeline(request.domain)
    background_tasks.add_task(run_pipeline, session.id)

    logger.info(f"Pipeline {session.id} started for domain: {session.domain}")

    return PipelineResponse(
        pipeline_id=session.id,
        status=session.status,
        message=f"Pipeline started for {session.domain}",
    )


@router.get("/status/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    """Get current status of a pipeline."""
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return {
        "pipeline_id": session.id,
        "domain": session.domain,
        "status": session.status,
        "stages": {k: v.model_dump() for k, v in session.stages.items()},
        "total_companies": session.total_companies,
        "total_contacts": session.total_contacts,
        "total_emails_found": session.total_emails_found,
        "total_sent": session.total_sent,
        "total_failed": session.total_failed,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


@router.get("/summary/{pipeline_id}", response_model=PipelineSummary)
async def get_pipeline_summary(pipeline_id: str):
    """Get pipeline summary for review/approval."""
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return PipelineSummary(
        pipeline_id=session.id,
        domain=session.domain,
        status=session.status,
        total_companies=session.total_companies,
        total_contacts=session.total_contacts,
        total_emails_found=session.total_emails_found,
        total_sent=session.total_sent,
        total_failed=session.total_failed,
        stages={k: v.model_dump() for k, v in session.stages.items()},
        sample_contacts=session.contacts[:5],
    )


@router.post("/approve")
async def approve_pipeline(request: ApprovalRequest, background_tasks: BackgroundTasks):
    """Approve or cancel email sending."""
    session = store.get(request.pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    if not request.approved:
        from app.models.pipeline import PipelineStatus
        session.status = PipelineStatus.FAILED
        store.save(session)
        return {"message": "Pipeline cancelled by user"}

    background_tasks.add_task(execute_sending, request.pipeline_id)
    return {"message": "Email sending started", "pipeline_id": request.pipeline_id}


@router.get("/list")
async def list_pipelines():
    """List all pipeline sessions."""
    sessions = store.list_all()
    return [
        {
            "pipeline_id": s.id,
            "domain": s.domain,
            "status": s.status,
            "total_companies": s.total_companies,
            "total_contacts": s.total_contacts,
            "total_emails_found": s.total_emails_found,
            "created_at": s.created_at,
        }
        for s in sorted(sessions, key=lambda x: x.created_at, reverse=True)
    ]
