"""
Results API endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.config.store import store

router = APIRouter()


@router.get("/{pipeline_id}/companies")
async def get_companies(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"companies": [c.model_dump() for c in session.similar_companies]}


@router.get("/{pipeline_id}/contacts")
async def get_contacts(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"contacts": [c.model_dump() for c in session.contacts]}


@router.get("/{pipeline_id}/email-preview")
async def get_email_preview(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    preview = [
        {
            "contact": log.contact.model_dump(),
            "subject": log.subject,
            "body": log.body[:300] + "..." if len(log.body) > 300 else log.body,
        }
        for log in session.email_logs[:5]
    ]
    return {"preview": preview, "total": len(session.email_logs)}
