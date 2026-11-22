"""Pydantic schemas for the API.

⚠️ This file is THE DATA CONTRACT shared with the frontend: it must stay an
exact mirror of ``frontend/src/types.ts``. If you change a field here, remember
to make the equivalent change on the TypeScript side.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChordEvent(BaseModel):
    """A chord expressed both as a degree and as a chord name."""

    degree: str
    chord: str
    referenceMatches: int = 0
    example: tuple[str, ...] = ()


class DetectedChord(BaseModel):
    """A detected chord and its interval in seconds."""

    chord: str
    degree: str | None
    start: float
    end: float


class Suggestion(BaseModel):
    """Suggestion from the music engine for the continuation of the progression."""

    candidates: list[ChordEvent]
    rationale: str


class Analysis(BaseModel):
    """Full result of an audio analysis (``POST /api/analyze`` response)."""

    fileName: str
    keyRoot: str | None
    keyMode: Literal["major", "minor"] | None
    keyStatus: Literal["estimated", "tentative", "undetermined"] = "undetermined"
    alternativeKey: str | None = None
    progression: list[DetectedChord]
    suggestion: Suggestion


class ChatMessage(BaseModel):
    """A message in the conversation with the theory assistant."""

    id: str
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Request body for ``POST /api/chat``."""

    query: str
    history: list[ChatMessage] = Field(default_factory=list)
    analysis: Analysis | None = None


class ChatResponse(BaseModel):
    """Response from ``POST /api/chat``."""

    response: str
