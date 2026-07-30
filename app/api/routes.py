from __future__ import annotations

import logging
import json
from pathlib import Path as PathLib
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    CandidateResponse,
    ExtractCandidate,
    ExtractRequest,
    ExtractResponse,
    FeatureScores,
    ScoreRequest,
    ScoreResponse,
)
from app.database.models import MemoryRecord
from app.database.session import SessionLocal
from app.extractors.candidate_extractor import MemoryCandidateExtractor, RegexMemoryCandidateExtractor
from app.scoring.decision_engine import DecisionEngine
from app.scoring.feature_extractor import FeatureExtractor
from app.scoring.importance_engine import ImportanceScoringEngine
from app.scoring.memory_pipeline import MemoryScoringPipeline

LOGGER = logging.getLogger(__name__)
router = APIRouter()

candidate_extractor = RegexMemoryCandidateExtractor()
memory_candidate_extractor = MemoryCandidateExtractor()
feature_extractor = FeatureExtractor()
weights_path = PathLib(__file__).resolve().parents[1] / "config" / "weights.json"
with weights_path.open("r", encoding="utf-8") as handle:
    weight_config = json.load(handle)
thresholds_path = PathLib(__file__).resolve().parents[1] / "config" / "decision_thresholds.json"
with thresholds_path.open("r", encoding="utf-8") as handle:
    threshold_config = json.load(handle)
importance_engine = ImportanceScoringEngine(weight_config=weight_config, thresholds=threshold_config)
decision_engine = DecisionEngine(thresholds=threshold_config)
pipeline = MemoryScoringPipeline(
    sentence_splitter=None,
    candidate_extractor=candidate_extractor,
    feature_extractor=feature_extractor,
    importance_engine=importance_engine,
    decision_engine=decision_engine,
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/extract", response_model=ExtractResponse)
def extract_memory_candidates(payload: ExtractRequest) -> ExtractResponse:
    try:
        candidates = memory_candidate_extractor.extract(payload.conversation)
        return ExtractResponse(
            candidates=[
                ExtractCandidate(
                    text=candidate.text,
                    reason=candidate.reason,
                    combined_score=round(candidate.combined_score, 4),
                )
                for candidate in candidates
            ]
        )
    except Exception as exc:
        LOGGER.exception("Error while extracting memory candidates")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/score", response_model=ScoreResponse)
def score_conversation(payload: ScoreRequest) -> ScoreResponse:
    try:
        result = pipeline.process(payload.conversation, agent_profile=payload.agent_profile or "Research Assistant")
        return ScoreResponse(candidate_memories=result)
    except Exception as exc:
        LOGGER.exception("Error while scoring conversation")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/memory")
def get_all_memories() -> list[dict[str, object]]:
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
    except Exception as exc:
        LOGGER.exception("Error fetching memories")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    finally:
        db.close()


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: Annotated[int, Path(title="Memory id")]) -> dict[str, str]:
    db = SessionLocal()
    try:
        row = db.query(MemoryRecord).filter(MemoryRecord.id == memory_id).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
        db.delete(row)
        db.commit()
        return {"message": "Memory deleted"}
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Error deleting memory")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    finally:
        db.close()
