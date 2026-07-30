from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import MemoryRecord
from app.database.session import SessionLocal

LOGGER = logging.getLogger(__name__)


class MemoryService:
    """Persistence service for storing and retrieving memory records."""

    def list_memories(self) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            rows = db.query(MemoryRecord).order_by(MemoryRecord.timestamp.desc()).all()
            return [
                {
                    "id": row.id,
                    "text": row.text,
                    "importance_score": row.importance_score,
                    "decision": row.decision,
                    "explanation": row.explanation,
                    "timestamp": row.timestamp.isoformat(),
                    "frequency": row.frequency,
                    "agent_profile": row.agent_profile,
                }
                for row in rows
            ]
        finally:
            db.close()

    def delete_memory(self, memory_id: int) -> bool:
        db = SessionLocal()
        try:
            record = db.query(MemoryRecord).filter(MemoryRecord.id == memory_id).first()
            if record is None:
                return False
            db.delete(record)
            db.commit()
            return True
        finally:
            db.close()
