from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    conversation: str = Field(..., min_length=1)
    agent_profile: Optional[str] = Field(default="Research Assistant")


class ExtractRequest(BaseModel):
    conversation: str = Field(..., min_length=1)


class ExtractCandidate(BaseModel):
    text: str
    reason: str
    combined_score: float


class ExtractResponse(BaseModel):
    candidates: list[ExtractCandidate]


class FeatureScores(BaseModel):
    preference: float
    frequency: float
    confidence: float
    task: float
    long_term: float
    recency: float


class CandidateResponse(BaseModel):
    text: str
    score: float
    decision: str
    features: FeatureScores
    explanation: str


class ScoreResponse(BaseModel):
    candidate_memories: list[CandidateResponse]
