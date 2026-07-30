from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.api.schemas import CandidateResponse, FeatureScores
from app.database.models import MemoryRecord
from app.database.session import SessionLocal
from app.extractors.base import MemoryCandidateExtractor
from app.scoring.decision_engine import DecisionEngine
from app.scoring.feature_extractor import FeatureExtractor, FeatureVector
from app.scoring.importance_engine import ImportanceScoringEngine

LOGGER = logging.getLogger(__name__)


class MemoryScoringPipeline:
    """Pipeline orchestration for conversation-to-memory decisioning."""

    def __init__(
        self,
        sentence_splitter: Optional[Any],
        candidate_extractor: MemoryCandidateExtractor,
        feature_extractor: FeatureExtractor,
        importance_engine: ImportanceScoringEngine,
        decision_engine: DecisionEngine,
    ) -> None:
        self._sentence_splitter = sentence_splitter
        self._candidate_extractor = candidate_extractor
        self._feature_extractor = feature_extractor
        self._importance_engine = importance_engine
        self._decision_engine = decision_engine

    def process(self, conversation: str, agent_profile: str = "Research Assistant") -> list[CandidateResponse]:
        candidates = self._candidate_extractor.extract(conversation)
        history = self._load_history(agent_profile)
        responses: list[CandidateResponse] = []
        for candidate in candidates:
            features = self._feature_extractor.extract_features(candidate, agent_profile=agent_profile, history=history)
            score = self._importance_engine.score(features)
            decision = self._decision_engine.decide(score)
            explanation = self._decision_engine.explain(score, self._feature_to_dict(features))
            response = CandidateResponse(
                text=candidate,
                score=round(score, 4),
                decision=decision,
                features=FeatureScores(**self._feature_to_dict(features)),
                explanation=explanation,
            )
            if decision in {"PERMANENT_MEMORY", "TEMPORARY_MEMORY"}:
                self._persist_memory(candidate, score, decision, explanation, agent_profile, features)
            responses.append(response)
        return responses

    def _persist_memory(self, text: str, score: float, decision: str, explanation: str, agent_profile: str, features: FeatureVector) -> None:
        db = SessionLocal()
        try:
            memory = MemoryRecord(
                text=text,
                importance_score=score,
                decision=decision,
                explanation=explanation,
                timestamp=datetime.utcnow(),
                frequency=features.frequency,
                agent_profile=agent_profile,
            )
            db.add(memory)
            db.commit()
            LOGGER.info("Stored memory decision=%s score=%.4f", decision, score)
        except Exception as exc:
            LOGGER.exception("Failed to persist memory")
            raise
        finally:
            db.close()

    def _load_history(self, agent_profile: str) -> list[str]:
        db = SessionLocal()
        try:
            rows = db.query(MemoryRecord).filter(MemoryRecord.agent_profile == agent_profile).all()
            return [row.text for row in rows]
        finally:
            db.close()

    @staticmethod
    def _feature_to_dict(features: FeatureVector) -> dict[str, float]:
        return {
            "preference": features.preference,
            "frequency": features.frequency,
            "confidence": features.confidence,
            "task": features.task,
            "long_term": features.long_term,
            "recency": features.recency,
        }
