"""Tests for the adaptation from recording analysis to HTTP schemas."""

from pathlib import Path

import pytest

from musaic.api import services
from musaic.pipeline import ChordSuggestion, DetectedChord, RecordingAnalysis


def test_parse_key() -> None:
    assert services._parse_key("C") == ("C", "major")
    assert services._parse_key("F#") == ("F#", "major")
    assert services._parse_key("Am") == ("A", "minor")
    assert services._parse_key("Cm") == ("C", "minor")


def test_analyze_audio_preserves_chord_timing(monkeypatch: pytest.MonkeyPatch) -> None:
    def analyze_recording(path: Path) -> RecordingAnalysis:
        assert path == Path("recording.wav")
        return RecordingAnalysis(
            key="Am",
            progression=[DetectedChord("Am", "i", 0.2, 1.7)],
            suggestions=[ChordSuggestion("E", "V")],
        )

    monkeypatch.setattr(services, "analyze_recording", analyze_recording)

    analysis = services.analyze_audio(Path("recording.wav"), "recording.wav")

    assert (analysis.keyRoot, analysis.keyMode) == ("A", "minor")
    assert analysis.progression[0].model_dump() == {
        "degree": "i",
        "chord": "Am",
        "start": 0.2,
        "end": 1.7,
    }
    assert analysis.suggestion.candidates[0].chord == "E"
