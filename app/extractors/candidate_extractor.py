from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from app.extractors.base import MemoryCandidateExtractor as MemoryCandidateExtractorBase
from app.services.sentence_splitter import SentenceSplitter

LOGGER = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore


@dataclass(frozen=True)
class MemoryCandidate:
    """Structured memory extraction result for downstream scoring stages."""

    text: str
    sentence_index: int
    rule_score: float
    semantic_score: float
    combined_score: float
    reason: str
    timestamp: str


class MemoryCandidateExtractor(MemoryCandidateExtractorBase):
    """Hybrid memory candidate extractor using rule-matching and semantic similarity."""

    def __init__(
        self,
        sentence_splitter: Optional[SentenceSplitter] = None,
        config_path: Optional[str] = None,
        semantic_model_name: str = "all-MiniLM-L6-v2",
        semantic_model: Optional[Any] = None,
    ) -> None:
        self._sentence_splitter = sentence_splitter or SentenceSplitter()
        self._config_path = Path(config_path or Path(__file__).resolve().parents[1] / "config" / "candidate_config.json")
        self._config = self._load_config(self._config_path)
        self._semantic_model_name = semantic_model_name
        self._semantic_model = semantic_model
        self._semantic_threshold = float(self._config.get("semantic_threshold", 0.55))
        self._rule_weight = float(self._config.get("rule_weight", 0.65))
        self._semantic_weight = float(self._config.get("semantic_weight", 0.35))
        self._rule_patterns = self._config.get("rule_patterns", [])
        self._excluded_phrases = self._config.get("excluded_phrases", [])
        self._prototype_sentences = self._config.get("prototype_sentences", [])

    def extract(self, conversation: str) -> list[MemoryCandidate]:
        """Extract long-term memory candidates from a conversation string."""
        if not isinstance(conversation, str) or not conversation.strip():
            return []

        sentences = self._sentence_splitter.split(conversation)
        candidates: list[MemoryCandidate] = []
        for index, sentence in enumerate(sentences, start=1):
            normalized = sentence.strip()
            if not normalized:
                continue

            lowered = normalized.lower().strip()
            if self._is_excluded(lowered):
                continue

            rule_score, rule_reason = self._rule_score(lowered)
            semantic_score, semantic_reason = self._semantic_score(normalized)
            combined_score = self._combine_scores(rule_score, semantic_score)

            if not self._should_keep(rule_score, semantic_score):
                continue

            candidate = MemoryCandidate(
                text=normalized,
                sentence_index=index,
                rule_score=round(rule_score, 4),
                semantic_score=round(semantic_score, 4),
                combined_score=round(combined_score, 4),
                reason=self._build_reason(rule_reason, semantic_reason, combined_score),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            candidates.append(candidate)

        LOGGER.info("Extracted %s memory candidates from conversation", len(candidates))
        return candidates

    def _load_config(self, config_path: Path) -> dict[str, Any]:
        try:
            with config_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            LOGGER.warning("Candidate config not found at %s; using empty defaults", config_path)
            return {}
        except json.JSONDecodeError:
            LOGGER.warning("Invalid candidate config at %s; using empty defaults", config_path)
            return {}

    def _is_excluded(self, sentence: str) -> bool:
        lowered = sentence.lower().strip()
        for phrase in self._excluded_phrases:
            pattern = re.compile(rf"\b{re.escape(phrase)}\b")
            if pattern.search(lowered):
                return True
        return False

    def _rule_score(self, sentence: str) -> tuple[float, str]:
        matches = [pattern for pattern in self._rule_patterns if pattern in sentence]
        if not matches:
            return 0.0, ""

        best_match = max(matches, key=len)
        score = min(1.0, 0.45 + (0.1 * len(best_match.split())))
        return score, f"Matched pattern: '{best_match}'"

    def _semantic_score(self, sentence: str) -> tuple[float, str]:
        if not self._prototype_sentences:
            return 0.0, ""

        if self._semantic_model is None:
            try:
                if SentenceTransformer is None:
                    raise ImportError("sentence-transformers is not installed")
                self._semantic_model = SentenceTransformer(self._semantic_model_name)
            except Exception as exc:
                LOGGER.warning("Semantic detector unavailable: %s", exc)
                return 0.0, "Semantic model unavailable"

        try:
            embeddings = self._semantic_model.encode([sentence, *self._prototype_sentences], convert_to_tensor=False)
            sentence_embedding = embeddings[0]
            prototype_embeddings = embeddings[1:]
            scores = []
            for prototype_embedding in prototype_embeddings:
                similarity = self._cosine_similarity(sentence_embedding, prototype_embedding)
                scores.append(similarity)
            best_similarity = max(scores) if scores else 0.0
            return best_similarity, f"Semantic similarity: {best_similarity:.2f}"
        except Exception as exc:
            LOGGER.warning("Semantic detection failed for '%s': %s", sentence, exc)
            return 0.0, "Semantic detection failed"

    @staticmethod
    def _cosine_similarity(a: Any, b: Any) -> float:
        try:
            a_vec = np.asarray(a, dtype=float)
            b_vec = np.asarray(b, dtype=float)
        except Exception:
            return 0.0

        if a_vec.ndim != 1 or b_vec.ndim != 1 or a_vec.shape != b_vec.shape:
            return 0.0

        a_norm = np.linalg.norm(a_vec)
        b_norm = np.linalg.norm(b_vec)
        if a_norm == 0 or b_norm == 0:
            return 0.0

        return float(np.dot(a_vec, b_vec) / (a_norm * b_norm))

    def _combine_scores(self, rule_score: float, semantic_score: float) -> float:
        return min(1.0, (self._rule_weight * rule_score) + (self._semantic_weight * semantic_score))

    def _should_keep(self, rule_score: float, semantic_score: float) -> bool:
        return rule_score > 0.0 or semantic_score >= self._semantic_threshold

    @staticmethod
    def _build_reason(rule_reason: str, semantic_reason: str, combined_score: float) -> str:
        parts = []
        if rule_reason:
            parts.append(rule_reason)
        if semantic_reason:
            parts.append(semantic_reason)
        parts.append(f"Combined score: {combined_score:.2f}")
        return "\n".join(parts)


class RegexMemoryCandidateExtractor(MemoryCandidateExtractorBase):
    """Backward-compatible rule-based extractor used by the existing scoring pipeline."""

    _IGNORED_PATTERNS = (
        r"^hello$",
        r"^thanks$",
        r"^thank you$",
        r"^okay$",
        r"^nice$",
        r"^bye$",
        r"^goodbye$",
        r"^hi$",
    )

    def extract(self, conversation: str) -> list[str]:
        """Split a conversation into sentences and keep only likely long-term memory sentences."""
        cleaned = re.sub(r"\s+", " ", conversation).strip()
        if not cleaned:
            return []

        sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", cleaned) if segment.strip()]
        candidates: list[str] = []
        for sentence in sentences:
            lowered = sentence.lower().strip()
            if self._is_ignored(lowered):
                continue
            if self._looks_like_memory(lowered):
                candidates.append(sentence)
        LOGGER.info("Extracted %s candidate memory sentences", len(candidates))
        return candidates

    def _is_ignored(self, sentence: str) -> bool:
        return any(re.fullmatch(pattern, sentence) for pattern in self._IGNORED_PATTERNS)

    def _looks_like_memory(self, sentence: str) -> bool:
        memory_markers = (
            "favorite",
            "prefer",
            "like",
            "love",
            "usually use",
            "work as",
            "research topic",
            "my name is",
            "i am",
            "birthday",
            "project is",
            "my goal",
            "i prefer",
            "i love",
            "i work",
            "my research",
            "my project",
            "i usually",
        )
        return any(marker in sentence for marker in memory_markers)


class LLMClassifierMemoryCandidateExtractor(MemoryCandidateExtractorBase):
    """Optional LLM-backed replacement for the rule-based extractor."""

    def __init__(self, classifier: Optional[object] = None) -> None:
        self._classifier = classifier

    def extract(self, conversation: str) -> list[str]:
        if self._classifier is None:
            LOGGER.warning("LLM classifier not configured; returning empty list")
            return []
        return []
