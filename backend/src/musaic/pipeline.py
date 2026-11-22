"""Shared analysis of piano recordings for the CLI and the API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from musaic.audio.chord_detector import detect_chords
from musaic.audio.transcriber import transcribe_audio
from musaic.engine.musical_engine import (
    chord_degrees,
    degrees_to_chords,
    estimate_key,
    rank_next_degrees,
)


@dataclass(frozen=True)
class DetectedChord:
    chord: str | None
    degree: str | None
    start: float
    end: float


@dataclass(frozen=True)
class ChordSuggestion:
    chord: str
    degree: str
    reference_matches: int = 0
    example: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecordingAnalysis:
    key: str | None
    progression: list[DetectedChord]
    suggestions: list[ChordSuggestion]
    key_status: Literal["estimated", "tentative", "undetermined"] = "undetermined"
    alternative_key: str | None = None


def analyze_recording(audio_path: str | Path) -> RecordingAnalysis:
    notes = transcribe_audio(audio_path)
    key_estimate = estimate_key(note["pitch"] for note in notes)
    key = key_estimate.key
    segments = detect_chords(notes)
    labeled = (segment for segment in segments if segment["chord"] is not None)
    degrees = chord_degrees(key, labeled) if key else iter(())
    progression = [
        DetectedChord(
            segment["chord"],
            next(degrees, None) if segment["chord"] is not None else None,
            segment["start"],
            segment["end"],
        )
        for segment in segments
    ]

    suggestions = []
    if key is not None:
        # Only match the confirmed suffix. An unresolved span could hide a chord change.
        known_degrees: list[str] = []
        for event in reversed(progression):
            if event.degree is None:
                break
            known_degrees.append(event.degree)
        known_degrees.reverse()
        for match in rank_next_degrees(known_degrees):
            for chord in degrees_to_chords(key, [match.degree]):
                suggestions.append(
                    ChordSuggestion(chord, match.degree, match.reference_matches, match.example)
                )

    return RecordingAnalysis(
        key, progression, suggestions, key_estimate.status, key_estimate.alternative
    )
