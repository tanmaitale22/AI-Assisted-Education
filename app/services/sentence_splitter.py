from __future__ import annotations

import logging
import re
from typing import Sequence

LOGGER = logging.getLogger(__name__)

try:
    import spacy  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    spacy = None

try:
    import nltk  # type: ignore
    from nltk.tokenize import sent_tokenize  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    nltk = None
    sent_tokenize = None


class SentenceSplitter:
    """Split conversation text into sentence-like units with spaCy -> nltk -> regex fallback."""

    def __init__(self, spacy_model: str = "en_core_web_sm") -> None:
        self._spacy_model = spacy_model
        self._nlp = None
        if spacy is not None:
            try:
                self._nlp = spacy.load(spacy_model)
            except OSError:
                LOGGER.warning("spaCy model %s not available; falling back to nltk/regex", spacy_model)
                self._nlp = None

    def split(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        if self._nlp is not None:
            return self._split_with_spacy(normalized)
        if nltk is not None and sent_tokenize is not None:
            return self._split_with_nltk(normalized)
        return self._split_with_regex(normalized)

    def _split_with_spacy(self, text: str) -> list[str]:
        assert self._nlp is not None
        doc = self._nlp(text)
        return [segment.text.strip() for segment in doc.sents if segment.text.strip()]

    def _split_with_nltk(self, text: str) -> list[str]:
        return [segment.strip() for segment in sent_tokenize(text) if segment.strip()]

    @staticmethod
    def _split_with_regex(text: str) -> list[str]:
        return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
