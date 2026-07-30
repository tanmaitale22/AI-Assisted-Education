from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.scoring.feature_extractor import FeatureVector

LOGGER = logging.getLogger(__name__)


class ImportanceScoringEngine:
    """Weighted scorer with configurable importances loaded from JSON config."""

    def __init__(self, weight_config: dict[str, float], thresholds: dict[str, float]) -> None:
        self._weights = weight_config
        self._thresholds = thresholds

    def score(self, features: FeatureVector) -> float:
        score = (
            self._weights["preference"] * features.preference
            + self._weights["long_term"] * features.long_term
            + self._weights["frequency"] * features.frequency
            + self._weights["task"] * features.task
            + self._weights["confidence"] * features.confidence
            + self._weights["recency"] * features.recency
        )
        LOGGER.info("Computed importance score: %.4f", score)
        return max(0.0, min(1.0, score))

    @staticmethod
    def load_config() -> dict[str, Any]:
        config_path = Path(__file__).resolve().parents[1] / "config" / "weights.json"
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
