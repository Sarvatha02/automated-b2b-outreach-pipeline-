"""
In-memory store for pipeline sessions.
In production, replace with Redis or a database.
"""

from typing import Dict, Optional
from app.models.pipeline import PipelineSession


class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, PipelineSession] = {}

    def get(self, pipeline_id: str) -> Optional[PipelineSession]:
        return self._sessions.get(pipeline_id)

    def save(self, session: PipelineSession) -> None:
        from datetime import datetime
        session.updated_at = datetime.utcnow()
        self._sessions[session.id] = session

    def delete(self, pipeline_id: str) -> None:
        self._sessions.pop(pipeline_id, None)

    def list_all(self) -> list:
        return list(self._sessions.values())


# Singleton instance
store = SessionStore()
