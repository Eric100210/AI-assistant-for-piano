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


def voicing(pitches: tuple[int, ...], start: float, end: float) -> list[MidiNote]:
    return [{"pitch": pitch, "start": start, "end": end} for pitch in pitches]


def test_passing_notes_keep_the_background_chord() -> None:
    notes = (
        voicing((48, 64, 67), 0.0, 1.0)
        + voicing((74,), 0.35, 0.57)
        + voicing((47,), 0.6, 0.7)
        + voicing((41, 60, 69), 1.0, 1.6)
    )

    assert detect_chords(notes) == [
        {"chord": "C", "start": 0.0, "end": 1.0},
        {"chord": "F", "start": 1.0, "end": 1.6},
    ]


def test_coordinated_fast_change_is_preserved() -> None:
    notes = (
        voicing((48, 64, 67), 0.0, 0.5)
        + voicing((43, 62, 71), 0.5, 0.6)
        + voicing((41, 60, 69), 0.6, 1.2)
    )

    assert [segment["chord"] for segment in detect_chords(notes)] == ["C", "G", "F"]


def test_seventh_attacked_with_the_chord_is_kept() -> None:
    assert detect_chords(voicing((48, 64, 67, 70), 0, 0.5))[0]["chord"] == "C7"


def test_ambiguous_bass_and_voice_have_no_chord_label() -> None:
    notes = voicing((48, 64, 67), 0, 0.5) + voicing((42, 60), 0.5, 0.9)
    assert detect_chords(notes)[-1] == {"chord": None, "start": 0.5, "end": 0.9}
    assert detect_chords(voicing((60,), 0, 0.9)) == []


def test_suggestions_use_the_confirmed_harmonic_suffix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from musaic import pipeline
    from musaic.engine.musical_engine import KeyEstimate

    notes = (
        voicing((48, 64, 67), 0.0, 0.5)
        + voicing((74,), 0.2, 0.43)
        + voicing((43, 62, 71), 0.5, 1.0)
        + voicing((45, 60, 64), 1.0, 1.5)
    )
    monkeypatch.setattr(pipeline, "transcribe_audio", lambda _: notes)
    monkeypatch.setattr(pipeline, "estimate_key", lambda _: KeyEstimate("C", "estimated"))

    result = pipeline.analyze_recording("recording.wav")
    assert [event.chord for event in result.progression] == ["C", "G", "Am"]
    assert [event.chord for event in result.suggestions] == ["F", "G"]

    notes.extend(voicing((42, 60), 1.5, 2.0))
    result = pipeline.analyze_recording("recording.wav")
    assert result.progression[-1].chord is None
    assert result.suggestions == []


def test_brief_sounding_gap_bridges_same_chord() -> None:
    notes = (
        voicing((48,), 0.0, 1.0)
        + voicing((64, 67), 0.0, 0.5)
        + voicing((74,), 0.5, 0.6)
        + voicing((64, 67), 0.6, 1.0)
    )
    assert detect_chords(notes) == [{"chord": "C", "start": 0.0, "end": 1.0}]


def test_suggestions_reuse_confirmed_chords_before_unclear_harmony(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from musaic import pipeline
    from musaic.audio.chord_detector import ChordSegment
    from musaic.engine.musical_engine import KeyEstimate

    chords = ["Cm", "G#", "Csus2", "G#", None, "A#", "Gm"]
    segments: list[ChordSegment] = [
        {"chord": chord, "start": float(index), "end": float(index + 1)}
        for index, chord in enumerate(chords)
    ]
    monkeypatch.setattr(pipeline, "transcribe_audio", lambda _: [])
    monkeypatch.setattr(pipeline, "detect_chords", lambda _: segments)
    monkeypatch.setattr(pipeline, "estimate_key", lambda _: KeyEstimate("Gm", "estimated"))

    result = pipeline.analyze_recording("recording.wav")

    assert [event.chord for event in result.progression] == chords
    assert [(event.chord, event.match_kind) for event in result.suggestions] == [
        ("D", "gap"),
        ("A#", "gap"),
    ]
    assert result.suggestions[0].example == ("i", "iv", "i", "V")
