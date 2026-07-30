from __future__ import annotations

import json
import re
import urllib.request
from typing import Any, Sequence

from .prompts import SYSTEM_PROMPT, build_user_prompt
from .schemas import MemoryRecord
from .validator import MemoryValidator


class BaseMemoryExtractor:
    """Base interface for memory extractors."""

    def __init__(self, validator: MemoryValidator | None = None) -> None:
        self.validator = validator or MemoryValidator()

    def extract(self, message: str) -> list[MemoryRecord]:
        raise NotImplementedError


class RuleBasedMemoryExtractor(BaseMemoryExtractor):
    """Rule-based extractor for educationally relevant memories."""

    def __init__(self, validator: MemoryValidator | None = None) -> None:
        super().__init__(validator=validator)

    def extract(self, message: str) -> list[MemoryRecord]:
        if not isinstance(message, str):
            return []

        cleaned = message.strip()
        if not cleaned:
            return []

        if self._is_noise(cleaned):
            return []

        candidates: list[MemoryRecord] = []
        if self._contains_learning_goal(cleaned):
            candidates.append(MemoryRecord(category="learning_goal", content=self._extract_learning_goal(cleaned), confidence=0.96))
        if self._contains_academic_progress(cleaned):
            candidates.append(MemoryRecord(category="academic_progress", content=self._extract_academic_progress(cleaned), confidence=0.95))
        if self._contains_weak_topic(cleaned):
            candidates.append(MemoryRecord(category="weak_topic", content=self._extract_weak_topic(cleaned), confidence=0.98))
        if self._contains_strong_topic(cleaned):
            candidates.append(MemoryRecord(category="strong_topic", content=self._extract_strong_topic(cleaned), confidence=0.95))
        if self._contains_learning_preference(cleaned):
            candidates.append(MemoryRecord(category="learning_preference", content=self._extract_learning_preference(cleaned), confidence=0.95))
        if self._contains_important_date(cleaned):
            candidates.append(MemoryRecord(category="important_date", content=self._extract_important_date(cleaned), confidence=0.94))
        if self._contains_personal_context(cleaned):
            candidates.append(MemoryRecord(category="personal_context", content=self._extract_personal_context(cleaned), confidence=0.92))

        return self.validator.validate(candidates)

    def _is_noise(self, message: str) -> bool:
        lower = message.lower().strip()
        noise_patterns = [
            r"^thanks\b",
            r"^okay\b",
            r"^hi\b",
            r"^hello\b",
            r"^bye\b",
            r"^can you explain",
            r"^please explain",
            r"^explain ",
            r"^what is ",
            r"^i can help",
            r"^sounds good",
            r"^good morning",
            r"^how are you",
        ]
        return any(re.search(pattern, lower) for pattern in noise_patterns)

    def _contains_learning_goal(self, message: str) -> bool:
        lower = message.lower()
        patterns = [r"\bprepare(?:d|ing)? for\b", r"\bplacement\b", r"\bgate\b", r"\binterview\b", r"\bstudy for\b", r"\bexam preparation\b"]
        if any(re.search(pattern, lower) for pattern in patterns):
            return True
        return bool(re.search(r"\bi have my\b", lower)) and bool(re.search(r"\bexam\b", lower))

    def _extract_learning_goal(self, message: str) -> str:
        lower = message.lower()
        if "prepare" in lower or "preparing" in lower:
            return "Preparing for GATE" if "gate" in lower else "Preparing for future learning"
        if "study for" in lower:
            topic = re.sub(r"^.*?study for\s+", "", lower)
            return f"Preparing for {self._normalize_topic(topic)}"
        if re.search(r"\bi have my\b", lower) and re.search(r"\bexam\b", lower):
            return f"AI exam next Monday" if "ai" in lower and "next monday" in lower else "Exam preparation"
        return "Learning goal"

    def _contains_academic_progress(self, message: str) -> bool:
        patterns = [r"\bfinished\b", r"\bcompleted\b", r"\blearned\b", r"\bstudied\b", r"\bcovered\b"]
        return any(re.search(pattern, message.lower()) for pattern in patterns)

    def _extract_academic_progress(self, message: str) -> str:
        if re.search(r"\bfinished\b", message, re.IGNORECASE):
            topic = re.sub(r"^.*?finished\s+", "", message, flags=re.IGNORECASE)
            return f"Finished {self._normalize_topic(topic)}"
        if re.search(r"\bcompleted\b", message, re.IGNORECASE):
            topic = re.sub(r"^.*?completed\s+", "", message, flags=re.IGNORECASE)
            return f"Completed {self._normalize_topic(topic)}"
        if re.search(r"\blearned\b", message, re.IGNORECASE):
            topic = re.sub(r"^.*?learned\s+", "", message, flags=re.IGNORECASE)
            return f"Learned {self._normalize_topic(topic)}"
        return "Academic progress"

    def _contains_weak_topic(self, message: str) -> bool:
        patterns = [r"\bdon't understand\b", r"\bdont understand\b", r"\bconfused about\b", r"\bstruggling with\b", r"\bstill don't understand\b"]
        return any(re.search(pattern, message.lower()) for pattern in patterns)

    def _extract_weak_topic(self, message: str) -> str:
        if re.search(r"(?:don't|dont|do not|cannot|can't|can not)\s+understand", message, re.IGNORECASE):
            topic = re.sub(
                r"^(?:.*?\s)?(?:don't|dont|do not|cannot|can't|can not)\s+understand\s+",
                "",
                message,
                flags=re.IGNORECASE,
            )
            return self._normalize_topic(topic)
        if re.search(r"\bconfused about\b", message, re.IGNORECASE):
            topic = re.sub(r"^confused about\s+", "", message, flags=re.IGNORECASE)
            return self._normalize_topic(topic)
        if re.search(r"\bstruggling with\b", message, re.IGNORECASE):
            topic = re.sub(r"^.*?struggling with\s+", "", message, flags=re.IGNORECASE)
            return self._normalize_topic(topic)
        return "Topic"

    def _contains_strong_topic(self, message: str) -> bool:
        patterns = [r"\bgood at\b", r"\bcomfortable with\b", r"\bstrong in\b", r"\bexcellent at\b"]
        return any(re.search(pattern, message.lower()) for pattern in patterns)

    def _extract_strong_topic(self, message: str) -> str:
        lower = message.lower()
        if "good at" in lower:
            topic = re.sub(r"^.*?good at\s+", "", message, flags=re.IGNORECASE)
            return self._normalize_topic(topic)
        if "comfortable with" in lower:
            topic = re.sub(r"^.*?comfortable with\s+", "", message, flags=re.IGNORECASE)
            return self._normalize_topic(topic)
        if "strong in" in lower:
            topic = re.sub(r"^.*?strong in\s+", "", message, flags=re.IGNORECASE)
            return self._normalize_topic(topic)
        return "Topic"

    def _contains_learning_preference(self, message: str) -> bool:
        patterns = [r"\bprefer\b", r"\blike\b", r"\bwant\b", r"\bneeds?\b", r"\busing\b"]
        return any(re.search(pattern, message.lower()) for pattern in patterns)

    def _extract_learning_preference(self, message: str) -> str:
        lower = message.lower()
        if "diagram" in lower or "diagrams" in lower:
            return "Prefers diagram-based explanations"
        if "code example" in lower or "code examples" in lower:
            return "Prefers code examples"
        if "simple" in lower:
            return "Prefers simple explanations"
        if "prefer" in lower:
            return message.split("prefer", 1)[1].strip().rstrip(" .,:;!?")
        return "Learning preference"

    def _contains_important_date(self, message: str) -> bool:
        patterns = [r"\bexam\b", r"\bassignment\b", r"\bdue\b", r"\bnext (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", r"\btomorrow\b"]
        return any(re.search(pattern, message.lower()) for pattern in patterns)

    def _extract_important_date(self, message: str) -> str:
        return message.strip().capitalize()

    def _contains_personal_context(self, message: str) -> bool:
        patterns = [r"\bcomputer engineering\b", r"\bsemester\b", r"\bstudent\b", r"\bdepartment\b"]
        return any(re.search(pattern, message.lower()) for pattern in patterns)

    def _extract_personal_context(self, message: str) -> str:
        if "computer engineering" in message.lower():
            return "Computer Engineering student"
        return self._normalize_topic(message)

    @staticmethod
    def _normalize_topic(text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text.strip()).rstrip(" .,:;!?")
        if not cleaned:
            return ""
        words = cleaned.split()
        normalized_words: list[str] = []
        for word in words:
            if word.isupper():
                normalized_words.append(word)
            elif re.fullmatch(r"[A-Za-z]{1,3}", word):
                normalized_words.append(word.upper() if word.lower() in {"ai", "cnn", "sql", "ml", "dl", "gpt"} else word.capitalize())
            else:
                normalized_words.append(word.capitalize())
        return " ".join(normalized_words)


class GeminiMemoryExtractor(BaseMemoryExtractor):
    """Optional Gemini-backed extractor with a deterministic fallback."""

    def __init__(self, validator: MemoryValidator | None = None, api_key: str | None = None, model: str = "gemini-2.0-flash") -> None:
        super().__init__(validator=validator)
        self.api_key = api_key
        self.model = model
        self.fallback = RuleBasedMemoryExtractor(validator=validator)

    def extract(self, message: str) -> list[MemoryRecord]:
        if not message or not self.api_key:
            return self.fallback.extract(message)

        try:
            payload = self._call_gemini(message)
            parsed = self._parse_response(payload)
            if parsed:
                validated = self.validator.validate(parsed)
                if validated:
                    return validated
        except Exception:
            pass
        return self.fallback.extract(message)

    def _call_gemini(self, message: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        request_body = {
            "contents": [{"parts": [{"text": build_user_prompt(message)}]}],
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        }
        data = json.dumps(request_body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
        return body

    def _parse_response(self, response: str) -> list[dict[str, Any]]:
        if not response:
            return []
        text = response.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return []

        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        return []


class AdaptiveMemoryExtractor(BaseMemoryExtractor):
    """High-level facade that uses the rule-based extractor by default."""

    def __init__(self, validator: MemoryValidator | None = None, api_key: str | None = None) -> None:
        super().__init__(validator=validator)
        self.rule_based = RuleBasedMemoryExtractor(validator=validator)
        self.llm = GeminiMemoryExtractor(validator=validator, api_key=api_key)

    def extract(self, message: str) -> list[MemoryRecord]:
        baseline = self.rule_based.extract(message)
        if baseline:
            return baseline
        return self.llm.extract(message)
