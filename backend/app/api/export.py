"""
Export endpoints - CSV and JSON.
"""

import csv
import io
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.config.store import store

router = APIRouter()


@router.get("/{pipeline_id}/contacts/csv")
async def export_contacts_csv(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["name", "job_title", "company", "domain", "linkedin_url", "email", "email_verified"])
    writer.writeheader()
    for c in session.contacts:
        writer.writerow(c.model_dump())

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=contacts_{pipeline_id[:8]}.csv"},
    )


@router.get("/{pipeline_id}/contacts/json")
async def export_contacts_json(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return JSONResponse(content={"contacts": [c.model_dump() for c in session.contacts]})


@router.get("/{pipeline_id}/email-logs/csv")
async def export_email_logs_csv(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["name", "email", "company", "job_title", "subject", "status", "sent_at", "error"])
    writer.writeheader()
    for log in session.email_logs:
        writer.writerow({
            "name": log.contact.name,
            "email": log.contact.email,
            "company": log.contact.company,
            "job_title": log.contact.job_title,
            "subject": log.subject,
            "status": log.status,
            "sent_at": str(log.sent_at) if log.sent_at else "",
            "error": log.error or "",
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=email_logs_{pipeline_id[:8]}.csv"},
    )


@router.get("/{pipeline_id}/full/json")
async def export_full_json(pipeline_id: str):
    session = store.get(pipeline_id)
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return JSONResponse(content={
        "pipeline_id": session.id,
        "domain": session.domain,
        "status": session.status,
        "summary": {
            "total_companies": session.total_companies,
            "total_contacts": session.total_contacts,
            "total_emails_found": session.total_emails_found,
            "total_sent": session.total_sent,
            "total_failed": session.total_failed,
        },
        "companies": [c.model_dump() for c in session.similar_companies],
        "contacts": [c.model_dump() for c in session.contacts],
        "email_logs": [
            {
                "contact": log.contact.model_dump(),
                "subject": log.subject,
                "status": log.status,
                "sent_at": str(log.sent_at) if log.sent_at else None,
                "error": log.error,
            }
            for log in session.email_logs
        ],
    })
