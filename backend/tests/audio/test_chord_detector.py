import pytest

from musaic.audio.chord_detector import detect_chords
from musaic.audio.transcriber import MidiNote


def test_chord_timestamps_follow_onsets_and_preserve_silent_gaps() -> None:
    notes: list[MidiNote] = [
        {"pitch": pitch, "start": start, "end": start + 0.5}
        for start in (1.0, 2.0)
        for pitch in (60, 64, 67)
    ]

    chords = detect_chords(notes)

    assert [str(segment["chord"]) for segment in chords] == ["C", "C"]
    assert [segment["start"] for segment in chords] == pytest.approx([1.0, 2.0])
    assert chords[0]["end"] < chords[1]["start"]
