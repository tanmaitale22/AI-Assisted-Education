from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryCandidateExtractor(ABC):
    """Interface for extracting memory candidate sentences from conversation text."""

    @abstractmethod
    def extract(self, conversation: str) -> list[str]:
        """Return candidate sentences likely to become memory."""
