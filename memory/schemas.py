from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

CategoryName = Literal[
    "learning_goal",
    "academic_progress",
    "weak_topic",
    "strong_topic",
    "learning_preference",
    "important_date",
    "personal_context",
]

ALLOWED_CATEGORIES = {
    "learning_goal",
    "academic_progress",
    "weak_topic",
    "strong_topic",
    "learning_preference",
    "important_date",
    "personal_context",
}


class MemoryRecord(BaseModel):
    """A validated memory candidate that can be stored for future personalization."""

    category: str = Field(..., description="Memory category")
    content: str = Field(..., description="Normalized memory content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the extraction")

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("category must be a string")
        cleaned = value.strip().lower().replace("-", "_").replace(" ", "_")
        if cleaned in ALLOWED_CATEGORIES:
            return cleaned
        if cleaned == "learning_goal":
            return "learning_goal"
        if cleaned == "academic_progress":
            return "academic_progress"
        if cleaned == "weak_topic":
            return "weak_topic"
        if cleaned == "strong_topic":
            return "strong_topic"
        if cleaned == "learning_preference":
            return "learning_preference"
        if cleaned == "important_date":
            return "important_date"
        if cleaned == "personal_context":
            return "personal_context"
        raise ValueError("invalid category")

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("content must be a string")
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("content cannot be empty")
        return cleaned

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 2)
