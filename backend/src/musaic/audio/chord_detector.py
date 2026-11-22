"""Track the harmony of transcribed piano notes over time."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import TypedDict

from musaic.audio.transcriber import MidiNote
from musaic.config import SEMIS

FRAME_SECONDS = 0.05
CHANGE_FRAMES = 3
MIN_UNCERTAIN_SECONDS = CHANGE_FRAMES * FRAME_SECONDS
MIN_NOTE_SECONDS = 0.075
SUSTAIN_SECONDS = 0.25
ONSET_TOLERANCE = 0.06


class ChordSegment(TypedDict):
    chord: str | None  # None marks a passage with harmonic evidence but no reliable label.
    start: float
    end: float


@dataclass(frozen=True)
class Harmony:
    name: str
    root: int
    tones: frozenset[int]
    seventh: int | None


CHORD_SHAPES = (
    ("", (0, 4, 7)),
    ("m", (0, 3, 7)),
    ("dim", (0, 3, 6)),
    ("aug", (0, 4, 8)),
    ("sus2", (0, 2, 7)),
    ("sus4", (0, 5, 7)),
    ("7", (0, 4, 7, 10)),
    ("maj7", (0, 4, 7, 11)),
    ("m7", (0, 3, 7, 10)),
    ("m7b5", (0, 3, 6, 10)),
    ("dim7", (0, 3, 6, 9)),
)

HARMONIES = tuple(
    Harmony(
        name + suffix,
        root,
        frozenset((root + interval) % 12 for interval in intervals),
        (root + intervals[-1]) % 12 if len(intervals) == 4 else None,
    )
    for root, name in enumerate(SEMIS)
    for suffix, intervals in CHORD_SHAPES
)


def active_notes_by_frame(
    notes: Sequence[MidiNote], duration: float
) -> Iterator[list[MidiNote]]:
    ordered = sorted(notes, key=lambda note: note["start"])
    active: list[MidiNote] = []
    next_note = 0
    index = 0
    while index * FRAME_SECONDS < duration:
        start = index * FRAME_SECONDS
        center = (start + min(start + FRAME_SECONDS, duration)) / 2
        active = [note for note in active if note["end"] > center]
        while next_note < len(ordered) and ordered[next_note]["start"] <= center:
            note = ordered[next_note]
            if note["end"] > center:
                active.append(note)
            next_note += 1
        yield active
        index += 1


def select_harmony(
    notes: Sequence[MidiNote], center: float, current: Harmony | None
) -> tuple[Harmony | None, bool]:
    """Return the strongest local harmony and whether its onset supports a fast change."""
    weights: dict[int, float] = {}
    fresh_tones: set[int] = set()
    for note in notes:
        pitch_class = note["pitch"] % 12
        weight = min((note["end"] - note["start"]) / SUSTAIN_SECONDS, 1.0)
        weights[pitch_class] = max(weight, weights.get(pitch_class, 0))
        if center - note["start"] <= ONSET_TOLERANCE:
            fresh_tones.add(pitch_class)

    bass_pool = [note for note in notes if note["end"] - note["start"] >= 0.12] or notes
    bass_note = min(bass_pool, key=lambda note: note["pitch"])
    bass = bass_note["pitch"] % 12
    fresh_bass = center - bass_note["start"] <= ONSET_TOLERANCE

    scores: list[tuple[float, Harmony, bool]] = []
    for harmony in HARMONIES:
        if bass not in harmony.tones or not harmony.tones <= weights.keys():
            continue

        seventh = harmony.seventh
        if seventh is not None and (
            weights[seventh] < 0.7
            or (harmony != current and not (fresh_bass and harmony.tones <= fresh_tones))
        ):
            continue

        outside = max(
            (weight for tone, weight in weights.items() if tone not in harmony.tones),
            default=0.0,
        )
        fit = sum(weights[tone] for tone in harmony.tones) / len(harmony.tones)
        bass_bonus = 0.35 if harmony.root == bass else 0.0
        together = fresh_bass and len(harmony.tones & fresh_tones) >= 3
        scores.append((fit + bass_bonus - 0.24 * outside, harmony, together))

    scores.sort(key=lambda candidate: candidate[0], reverse=True)
    if scores:
        score, best, together = scores[0]
        margin = score - scores[1][0] if len(scores) > 1 else float("inf")
        if margin >= 0.10 and (current is None or best == current or together or margin >= 0.24):
            return best, together

    if current and bass in current.tones:
        support = sum(weights[tone] for tone in current.tones if tone in weights)
        if support >= 1.1:
            return current, False

    return None, False


def bridge_passing_notes(
    decisions: list[tuple[Harmony | None, bool]], sounding: list[bool]
) -> None:
    """Bridge short sounding gaps only when the same harmony resumes."""
    previous: Harmony | None = None
    previous_index = 0
    for index, (harmony, _) in enumerate(decisions):
        if harmony is None:
            continue
        gap = index - previous_index - 1
        if (
            harmony == previous
            and 0 < gap <= CHANGE_FRAMES
            and all(sounding[previous_index + 1:index])
        ):
            decisions[previous_index + 1:index] = [(harmony, False)] * gap
        previous, previous_index = harmony, index


def detect_chords(notes: Sequence[MidiNote]) -> list[ChordSegment]:
    """Keep supported harmonies through passing notes and preserve unresolved spans."""
    duration = float(max((note["end"] for note in notes), default=0.0))
    decisions: list[tuple[Harmony | None, bool]] = []
    sounding: list[bool] = []
    current: Harmony | None = None
    pending: Harmony | None = None
    pending_start = 0

    for index, active in enumerate(active_notes_by_frame(notes, duration)):
        sounding.append(bool(active))
        pitches = {note["pitch"] % 12 for note in active}
        eligible = [note for note in active if note["end"] - note["start"] >= MIN_NOTE_SECONDS]
        if not active:
            current = None
        # Retain evidence about moving melody over a bass, while leaving monophonic spans unlabeled.
        uncertain = len(pitches) >= 2
        frame_start = index * FRAME_SECONDS
        center = (frame_start + min(frame_start + FRAME_SECONDS, duration)) / 2
        candidate, together = select_harmony(eligible, center, current) if eligible else (None, False)
        decisions.append((None, uncertain))

        if candidate is None:
            pending = None
            continue
        if candidate == current:
            decisions[-1] = (current, False)
            pending = None
            continue
        if pending != candidate:
            pending, pending_start = candidate, index
        if together or index - pending_start + 1 >= CHANGE_FRAMES:
            current = candidate
            for previous in range(pending_start, index + 1):
                decisions[previous] = (current, False)
            pending = None

    bridge_passing_notes(decisions, sounding)

    segments: list[ChordSegment] = []
    for index, (harmony, uncertain) in enumerate(decisions):
        if harmony is None and not uncertain:
            continue
        chord = harmony.name if harmony else None
        start = index * FRAME_SECONDS
        end = min((index + 1) * FRAME_SECONDS, duration)
        if segments and segments[-1]["chord"] == chord and segments[-1]["end"] == start:
            segments[-1]["end"] = end
        else:
            segments.append({"chord": chord, "start": start, "end": end})

    return [
        segment for segment in segments
        if segment["chord"] is not None
        or segment["end"] - segment["start"] + 1e-9 >= MIN_UNCERTAIN_SECONDS
    ]
