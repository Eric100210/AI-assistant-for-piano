"""Schémas Pydantic de l'API.

⚠️ Ce fichier est LE CONTRAT DE DONNÉES partagé avec le front : il doit rester
le miroir exact de ``frontend/src/types.ts``. Si tu modifies un champ ici,
pense à faire l'équivalent côté TypeScript.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChordEvent(BaseModel):
    """Un accord exprimé à la fois en degré et en nom."""

    degree: str
    chord: str


class Suggestion(BaseModel):
    """Suggestion du moteur musical pour la suite de la progression."""

    candidates: list[ChordEvent]
    rationale: str


class Analysis(BaseModel):
    """Résultat complet d'une analyse audio (réponse de ``POST /api/analyze``)."""

    fileName: str
    durationLabel: str
    keyRoot: str
    keyMode: Literal["majeur", "mineur"]
    confidence: float
    progression: list[ChordEvent]
    suggestion: Suggestion


class ChatMessage(BaseModel):
    """Un message de la conversation avec l'assistant théorique."""

    id: str
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Corps de la requête ``POST /api/chat``."""

    query: str
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Réponse de ``POST /api/chat``."""

    response: str
