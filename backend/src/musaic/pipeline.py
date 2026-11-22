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
    chord: str
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
    degrees = chord_degrees(key, segments) if key else (None for _ in segments)
    progression = [
        DetectedChord(str(segment["chord"]), degree, segment["start"], segment["end"])
        for segment, degree in zip(segments, degrees)
    ]

    suggestions = []
    if key is not None:
        known_degrees = [event.degree for event in progression if event.degree is not None]
        for match in rank_next_degrees(known_degrees):
            for chord in degrees_to_chords(key, [match.degree]):
                suggestions.append(
                    ChordSuggestion(chord, match.degree, match.reference_matches, match.example)
                )

    return RecordingAnalysis(
        key, progression, suggestions, key_estimate.status, key_estimate.alternative
    )
