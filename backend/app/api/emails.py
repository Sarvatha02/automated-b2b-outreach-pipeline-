"""
Email logs API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from app.config.store import store
from app.models.pipeline import EmailStatus

router = APIRouter()


@router.get("/{pipeline_id}/logs")
async def get_email_logs(
    pipeline_id: str,
    status: str = Query(None, description="Filter by status: sent, failed, pending"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    logs = session.email_logs

    if status:
        try:
            filter_status = EmailStatus(status)
            logs = [l for l in logs if l.status == filter_status]
        except ValueError:
            pass

    total = len(logs)
    paginated = logs[offset: offset + limit]

    return {
        "pipeline_id": pipeline_id,
        "total": total,
        "sent": sum(1 for l in session.email_logs if l.status == EmailStatus.SENT),
        "failed": sum(1 for l in session.email_logs if l.status == EmailStatus.FAILED),
        "pending": sum(1 for l in session.email_logs if l.status == EmailStatus.PENDING),
        "logs": [l.model_dump() for l in paginated],
    }
