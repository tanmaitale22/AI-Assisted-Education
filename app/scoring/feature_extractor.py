from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError:  # pragma: no cover - fallback path for lean runtimes
    SentenceTransformer = None  # type: ignore[assignment]

from sklearn.metrics.pairwise import cosine_similarity

LOGGER = logging.getLogger(__name__)


@dataclass
class FeatureVector:
    preference: float
    frequency: float
    confidence: float
    task: float
    long_term: float
    recency: float


class FeatureExtractor:
    """Compute normalized feature scores for memory candidates."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = SentenceTransformer(model_name) if SentenceTransformer is not None else None
        self._profile_keywords = self._load_agent_profiles()
        self._preference_terms = ["favorite", "prefer", "like", "love", "usually use"]
        self._certainty_patterns = ["i am", "my project is", "my name is", "my research topic is"]
        self._uncertainty_patterns = ["i think", "maybe", "i'm not sure", "perhaps"]

    def extract_features(self, text: str, agent_profile: str, history: list[str]) -> FeatureVector:
        pref = self._score_preference(text)
        long_term = self._score_long_term(text)
        freq = self._score_frequency(text, history)
        task = self._score_task(text, agent_profile)
        conf = self._score_confidence(text)
        recency = 1.0
        return FeatureVector(
            preference=self._clip(pref),
            frequency=self._clip(freq),
            confidence=self._clip(conf),
            task=self._clip(task),
            long_term=self._clip(long_term),
            recency=self._clip(recency),
        )

    def _score_preference(self, text: str) -> float:
        lower = text.lower()
        if any(term in lower for term in self._preference_terms):
            return 1.0
        return 0.0

    def _score_long_term(self, text: str) -> float:
        lower = text.lower()
        long_term_markers = [
            "favorite", "research topic", "project", "work as", "name", "goal", "birthday", "skills", "language", "profession", "software engineer", "research"
        ]
        matching = sum(1 for marker in long_term_markers if marker in lower)
        value = matching / max(1, len(long_term_markers))
        if any(marker in lower for marker in ["i am", "my name is", "my favorite", "research topic", "work as", "birthday", "software engineer", "my project"]):
            value += 0.5
        return min(1.0, value)

    def _score_frequency(self, text: str, history: list[str]) -> float:
        if not history:
            return 0.0
        if self._model is None:
            return float(max(1.0 if text.lower() == item.lower() else 0.0 for item in history))
        embeddings = self._model.encode([text, *history])
        sims = cosine_similarity([embeddings[0]], embeddings[1:])[0]
        return float(max(sims)) if len(sims) > 0 else 0.0

    def _score_task(self, text: str, agent_profile: str) -> float:
        keywords = self._profile_keywords.get(agent_profile, [])
        lower = text.lower()
        overlaps = [keyword for keyword in keywords if keyword in lower]
        base = min(1.0, len(overlaps) / max(1, len(keywords)))
        identity_markers = ["i am", "my name is", "my goal", "my project", "work as", "favorite", "research topic"]
        if any(marker in lower for marker in identity_markers) and overlaps:
            base = max(base, 0.8)
        if agent_profile == "Research Assistant" and any(term in lower for term in ["research", "topic", "paper", "goal", "project"]):
            base = max(base, 0.9)
        if agent_profile == "Coding Assistant" and any(term in lower for term in ["software engineer", "code", "python", "project", "language"]):
            base = max(base, 0.9)
        return min(1.0, base)

    def _score_confidence(self, text: str) -> float:
        lower = text.lower()
        if any(pattern in lower for pattern in self._certainty_patterns):
            return 1.0
        if any(pattern in lower for pattern in self._uncertainty_patterns):
            return 0.3
        return 0.6

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _load_agent_profiles() -> dict[str, list[str]]:
        config_path = Path(__file__).resolve().parents[1] / "config" / "agent_profiles.json"
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
