from __future__ import annotations

import re
from typing import Any, Sequence

from .schemas import ALLOWED_CATEGORIES, MemoryRecord


class MemoryValidator:
    """Validate, normalize, and deduplicate extracted memories."""

    def __init__(self) -> None:
        self._allowed_categories = ALLOWED_CATEGORIES

    def validate(self, records: Sequence[MemoryRecord | dict[str, Any]]) -> list[MemoryRecord]:
        normalized: list[MemoryRecord] = []
        seen: set[tuple[str, str]] = set()

        for raw in records:
            if isinstance(raw, MemoryRecord):
                record = raw
            elif isinstance(raw, dict):
                try:
                    record = MemoryRecord(**raw)
                except Exception:
                    continue
            else:
                continue

            category = self.normalize_category(record.category)
            content = self.normalize_content(category, record.content)
            confidence = round(max(0.0, min(1.0, float(record.confidence))), 2)

            if not content:
                continue
            if category not in self._allowed_categories:
                continue
            if not 0.0 <= confidence <= 1.0:
                continue

            dedupe_key = (category, content.lower())
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            normalized.append(MemoryRecord(category=category, content=content, confidence=confidence))

        return normalized

    def normalize_category(self, category: str) -> str:
        cleaned = category.strip().lower().replace("-", "_").replace(" ", "_")
        if cleaned in self._allowed_categories:
            return cleaned
        return ""

    def normalize_content(self, category: str, content: str) -> str:
        cleaned = re.sub(r"\s+", " ", content.strip())
        if not cleaned:
            return ""

        if category == "learning_preference":
            lowered = cleaned.lower()
            if "diagram" in lowered or "diagrams" in lowered:
                return "Prefers diagram-based explanations"
            if "code example" in lowered or "code examples" in lowered:
                return "Prefers code examples"
            if "simple" in lowered or "simple explanation" in lowered:
                return "Prefers simple explanations"
            return self._title_case(cleaned)

        if category == "weak_topic":
            lower = cleaned.lower()
            if "don't understand" in lower or "dont understand" in lower or "do not understand" in lower:
                topic = re.sub(r"^(?:i|we|they|you|she|he)?\s*(?:don't|dont|do not|cannot|can't|can not)\s+understand\s+", "", cleaned, flags=re.IGNORECASE)
                return self._title_case(topic)
            if "confused about" in lower:
                topic = re.sub(r"^confused about\s+", "", cleaned, flags=re.IGNORECASE)
                return self._title_case(topic)
            if "understand" in lower:
                topic = re.sub(r"^.*?understand\s+", "", cleaned, flags=re.IGNORECASE)
                return self._title_case(topic)
            return self._title_case(cleaned)

        if category == "strong_topic":
            lower = cleaned.lower()
            if "good at" in lower:
                topic = re.sub(r"^.*?good at\s+", "", cleaned, flags=re.IGNORECASE)
                return self._title_case(topic)
            if "comfortable with" in lower:
                topic = re.sub(r"^.*?comfortable with\s+", "", cleaned, flags=re.IGNORECASE)
                return self._title_case(topic)
            if "strong in" in lower:
                topic = re.sub(r"^.*?strong in\s+", "", cleaned, flags=re.IGNORECASE)
                return self._title_case(topic)
            return self._title_case(cleaned)

        if category == "learning_goal":
            lower = cleaned.lower()
            if "prepare" in lower or "preparing" in lower:
                topic = re.sub(r"^(?:i am|i'm|i\s+am|i\s+will|prepare|preparing)(?:\s+for)?\s*", "", cleaned, flags=re.IGNORECASE)
                if topic:
                    return f"Preparing for {self._normalize_goal_topic(topic)}"
                return "Preparing for future learning"
            return self._title_case(cleaned)

        if category == "academic_progress":
            lower = cleaned.lower()
            if "finished" in lower:
                topic = re.sub(r"^.*?finished\s+", "", cleaned, flags=re.IGNORECASE)
                return f"Completed {self._title_case(topic)}"
            if "learned" in lower:
                topic = re.sub(r"^.*?learned\s+", "", cleaned, flags=re.IGNORECASE)
                return f"Learned {self._title_case(topic)}"
            if "completed" in lower:
                topic = re.sub(r"^.*?completed\s+", "", cleaned, flags=re.IGNORECASE)
                return f"Completed {self._title_case(topic)}"
            return self._title_case(cleaned)

        if category == "important_date":
            lower = cleaned.lower()
            if "exam" in lower:
                return self._title_case(cleaned)
            if "assignment" in lower:
                return self._title_case(cleaned)
            return self._title_case(cleaned)

        if category == "personal_context":
            lower = cleaned.lower()
            if "computer engineering" in lower:
                return "Computer Engineering student"
            if "semester" in lower:
                return self._title_case(cleaned)
            return self._title_case(cleaned)

        return self._title_case(cleaned)

    @staticmethod
    def _title_case(text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text.strip()).rstrip(" .,:;!?")
        if not cleaned:
            return ""
        words = cleaned.split()
        normalized_words: list[str] = []
        for word in words:
            if word.isupper():
                normalized_words.append(word)
            elif re.fullmatch(r"[A-Za-z]{1,3}", word):
                normalized_words.append(word.upper() if word.lower() in {"ai", "cnn", "sql", "ml", "dl", "gpt", "gate"} else word.capitalize())
            else:
                normalized_words.append(word.capitalize())
        return " ".join(normalized_words)

    @staticmethod
    def _normalize_goal_topic(text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text.strip()).rstrip(" .,:;!?")
        if not cleaned:
            return ""
        lowered = cleaned.lower()
        if lowered in {"gate"}:
            return "GATE"
        if lowered in {"ai", "cnn", "sql", "ml", "dl", "gpt"}:
            return cleaned.upper()
        return MemoryValidator._title_case(cleaned)
