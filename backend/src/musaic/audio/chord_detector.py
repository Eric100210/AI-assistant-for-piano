from collections.abc import Iterable, Sequence
from math import isclose
from typing import TypedDict, cast

import numpy as np
from pychord import Chord, find_chords_from_notes

from musaic.audio.transcriber import MidiNote
from musaic.config import SEMIS

NOTE_THRESHOLD = 0.4  # threshold for considering a note as present in the window
WINDOW_SECONDS = 0.4
STEP_SECONDS = 0.1


class NoteWindow(TypedDict):
    time: float
    notes: list[str]


class ChordWindow(TypedDict):
    time: float
    chord: Chord | None


class ChordSegment(TypedDict):
    chord: Chord
    start: float
    end: float


def get_window_notes(
    notes: Iterable[MidiNote],
    t: float,
    window_size: float = WINDOW_SECONDS,
    threshold: float = NOTE_THRESHOLD,
) -> list[str]:
    window_end = t + window_size
    scores = [0.0] * 12

    for note in notes:
        overlap = max(0.0, min(note["end"], window_end) - max(note["start"], t))
        if overlap <= 0:
            continue
        score = min(1.0, overlap / window_size)
        pitch_class = note["pitch"] % 12

        # Avoid double counting same pitch class
        scores[pitch_class] = max(scores[pitch_class], score)

    return [SEMIS[i] for i, score in enumerate(scores) if score >= threshold]


def group_notes_by_time(
    notes: Sequence[MidiNote], frequency: float = STEP_SECONDS
) -> list[NoteWindow]:
    grouped_notes: list[NoteWindow] = []
    end = max((note["end"] for note in notes), default=0.0)
    for window_start in np.arange(0, end, frequency):
        t = cast(float, window_start)
        window_notes = get_window_notes(notes, t - WINDOW_SECONDS / 2)
        if window_notes:
            grouped_notes.append({"time": t, "notes": window_notes})

    return grouped_notes


def detect_chord_from_notes(notes: list[str]) -> Chord | None:
    if len(notes) < 3:
        return None

    pychord = find_chords_from_notes(notes)
    if pychord:
        return pychord[0]
    return None


def detect_chords_by_time(grouped_notes: Iterable[NoteWindow]) -> list[ChordWindow]:
    chords: list[ChordWindow] = []
    for group in grouped_notes:
        chords.append(
            {"time": group["time"], "chord": detect_chord_from_notes(group["notes"])}
        )

    return chords


def merge_chords(chords: Iterable[ChordWindow]) -> list[ChordSegment]:
    segments: list[ChordSegment] = []
    for chord_info in chords:
        chord = chord_info["chord"]
        time = chord_info["time"]

        if chord is None:
            continue

        if (
            segments
            and segments[-1]["chord"] == chord
            and isclose(segments[-1]["end"], time, abs_tol=1e-9)
        ):
            segments[-1]["end"] = time + STEP_SECONDS
        else:
            segments.append({"chord": chord, "start": time, "end": time + STEP_SECONDS})

    return segments


def detect_chords(notes: Sequence[MidiNote]) -> list[ChordSegment]:
    grouped_notes = group_notes_by_time(notes)
    chords = detect_chords_by_time(grouped_notes)
    merged_chords = merge_chords(chords)
    return merged_chords
