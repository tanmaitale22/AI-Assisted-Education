from __future__ import annotations

import logging
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)


class DecisionEngine:
    """Map a scalar importance score to a permanent, temporary, or discard decision."""

    def __init__(self, thresholds: dict[str, float]) -> None:
        self._thresholds = thresholds

    def decide(self, score: float) -> str:
        permanent = self._thresholds.get("permanent", 0.80)
        temporary = self._thresholds.get("temporary", 0.50)
        if score >= permanent:
            return "PERMANENT_MEMORY"
        if score >= temporary:
            return "TEMPORARY_MEMORY"
        return "DISCARD"

    def explain(self, score: float, features: dict[str, float]) -> str:
        reasons: list[str] = []
        if features.get("preference", 0.0) >= 0.7:
            reasons.append("High Preference")
        if features.get("long_term", 0.0) >= 0.6:
            reasons.append("Long-term relevance")
        if features.get("frequency", 0.0) >= 0.5:
            reasons.append("Frequently mentioned")
        if features.get("confidence", 0.0) >= 0.7:
            reasons.append("High confidence")
        if features.get("task", 0.0) >= 0.5:
            reasons.append("Task-relevant")
        if not reasons:
            reasons.append("Insufficient evidence for long-term storage")
        return f"Importance Score: {score:.2f}\nReason: " + "; ".join(reasons)
