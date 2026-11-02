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


class Suggestion(BaseModel):
    """Suggestion from the music engine for the continuation of the progression."""

    candidates: list[ChordEvent]
    rationale: str


class Analysis(BaseModel):
    """Full result of an audio analysis (``POST /api/analyze`` response)."""

    fileName: str
    durationLabel: str
    keyRoot: str
    keyMode: Literal["major", "minor"]
    confidence: float
    progression: list[ChordEvent]
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


class ChatResponse(BaseModel):
    """Response from ``POST /api/chat``."""

    response: str
