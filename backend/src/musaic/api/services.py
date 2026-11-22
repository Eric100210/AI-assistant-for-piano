"""Adapt application results to the HTTP schemas."""

from pathlib import Path
from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from musaic.api.schemas import (
    Analysis,
    ChatMessage,
    ChordEvent,
    DetectedChord,
    Suggestion,
)
from musaic.pipeline import analyze_recording


def _parse_key(key: str) -> tuple[str, Literal["major", "minor"]]:
    """Split the key returned by the engine into ``(root, mode)``.

    The engine returns e.g. ``"C"`` (major) or ``"Am"`` (minor): minor mode is
    indicated by a trailing ``"m"``.

    Expected examples:
        "C"  -> ("C",  "major")
        "F#" -> ("F#", "major")
        "Am" -> ("A",  "minor")
        "Cm" -> ("C",  "minor")
    """
    if key.endswith("m"):
        return key[:-1], "minor"
    return key, "major"


def analyze_audio(audio_path: Path, file_name: str) -> Analysis:
    result = analyze_recording(audio_path)
    key_root, key_mode = _parse_key(result.key) if result.key else (None, None)
    candidates = [
        ChordEvent(
            chord=event.chord,
            degree=event.degree,
            referenceMatches=event.reference_matches,
            example=event.example,
        )
        for event in result.suggestions
    ]

    if candidates:
        rationale = "Ranked by the number of matching progressions in the reference library."
        if result.key_status == "tentative":
            rationale += " These suggestions use the tentative key."
    elif not result.progression:
        rationale = "No chords were detected in this recording."
    else:
        rationale = "The music engine found no continuation for this progression."

    return Analysis(
        fileName=file_name,
        keyRoot=key_root,
        keyMode=key_mode,
        keyStatus=result.key_status,
        alternativeKey=result.alternative_key,
        progression=[
            DetectedChord(
                chord=event.chord, degree=event.degree, start=event.start, end=event.end
            )
            for event in result.progression
        ],
        suggestion=Suggestion(candidates=candidates, rationale=rationale),
    )


def build_history_messages(history: list[ChatMessage]) -> list[BaseMessage]:
    """Convertit l'historique (contrat API) en messages LangChain.

    Le front envoie l'historique à chaque requête : l'API reste sans état.
    """
    messages: list[BaseMessage] = []
    for message in history:
        if message.role == "user":
            messages.append(HumanMessage(content=message.content))
        else:
            messages.append(AIMessage(content=message.content))
    return messages
