import json
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, TypedDict, overload

import numpy as np

from musaic.config import PROGRESSIONS_JSON, SEMIS

SPECIFICATIONS = [
    "m",
    "maj",
    "2",
    "4",
    "5",
    "6",
    "7",
    "9",
    "sus",
    "dim",
    "aug",
    "add",
    "°",
]
CHROMATIC_DEGREES_MAJOR = [
    "I",
    "bII",
    "ii",
    "bIII",
    "iii",
    "IV",
    "#IV",
    "V",
    "bVI",
    "vi",
    "bVII",
    "vii°",
]

CHROMATIC_DEGREES_MINOR = [
    "i",
    "bII",
    "ii°",
    "III",
    "#III",
    "iv",
    "#IV",
    "v",
    "VI",
    "#VI",
    "VII",
    "#VII",
]

# Qualité « naturelle » de chaque degré selon le mode. C'est elle qui permet
# l'aller-retour degré <-> accord : un degré sans spécification (ex. "vi") doit
# se reconstruire avec sa qualité naturelle (ex. "Am", et non "A").
NATURAL_SPECIFICATIONS_MAJOR = {
    0: "",  # I
    2: "m",  # ii
    4: "m",  # iii
    5: "",  # IV
    7: "",  # V
    9: "m",  # vi
    11: "dim",  # vii°
}

NATURAL_SPECIFICATIONS_MINOR = {
    0: "m",  # i
    2: "dim",  # ii°
    3: "",  # III
    5: "m",  # iv
    7: "m",  # v
    8: "",  # VI
    10: "",  # VII
}

# Krumhansl-Kessler profiles
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)

MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)


ProgressionMode = Literal["major", "minor"]
MatchKind = Literal["exact", "similar", "short", "gap"]


class ProgressionMetadata(TypedDict, total=False):
    degres: list[str]
    tonalite: Literal["majeure", "mineure"]


class ProgressionRecord(TypedDict):
    metadata: ProgressionMetadata


@dataclass(frozen=True)
class KeyEstimate:
    key: str | None
    status: Literal["estimated", "tentative", "undetermined"]
    alternative: str | None = None


@dataclass(frozen=True)
class ReferenceProgression:
    degrees: tuple[str, ...]
    mode: ProgressionMode


@dataclass(frozen=True)
class RankedContinuation:
    degree: str
    reference_matches: int
    example: tuple[str, ...]
    match_kind: MatchKind


@lru_cache(maxsize=1)
def load_reference_progressions() -> tuple[ReferenceProgression, ...]:
    """Load the reference progressions once."""
    with open(PROGRESSIONS_JSON, encoding="utf-8") as source:
        content: list[ProgressionRecord] = json.load(source)
    return tuple(
        ReferenceProgression(
            tuple(metadata["degres"]),
            "minor" if metadata["tonalite"] == "mineure" else "major",
        )
        for record in content
        if (metadata := record["metadata"]).get("degres") and "tonalite" in metadata
    )


def estimate_key(pitches: Iterable[int]) -> KeyEstimate:
    """Compare pitch classes with the 24 Krumhansl-Kessler profiles."""
    note_profile = np.bincount([note % 12 for note in pitches], minlength=12)
    if not np.any(note_profile != note_profile[0]):
        return KeyEstimate(None, "undetermined")

    scores = [
        (float(np.corrcoef(note_profile, np.roll(profile, index))[0, 1]), key + suffix)
        for index, key in enumerate(SEMIS)
        for profile, suffix in ((MAJOR_PROFILE, ""), (MINOR_PROFILE, "m"))
    ]
    scores.sort(key=lambda entry: entry[0], reverse=True)
    (score, key), (second_score, alternative) = scores[:2]

    # Heuristics for sparse evidence and close fits. These scores are not probabilities.
    close = score - second_score < 0.06
    if np.count_nonzero(note_profile) < 4 or score < 0.60 or close:
        return KeyEstimate(key, "tentative", alternative if close else None)
    return KeyEstimate(key, "estimated")


def detect_key_from_notes(pitches: Iterable[int]) -> str | None:
    return estimate_key(pitches).key


@overload
def enharmonic_to_sharp(note: str) -> str: ...


@overload
def enharmonic_to_sharp(note: str | None) -> str | None: ...


def enharmonic_to_sharp(note: str | None) -> str | None:
    conversion: dict[str | None, str] = {
        "Db": "C#",
        "Eb": "D#",
        "Gb": "F#",
        "Ab": "G#",
        "Bb": "A#",
    }

    return conversion.get(note, note)


def split_chord(chord: object) -> tuple[str, str]:
    """
    Separate the root note from the chord specification.
    Examples :
        C       -> ("C", "")
        Am      -> ("A", "m")
        Cmaj7   -> ("C", "maj7")
        F#dim   -> ("F#", "dim")
        Bb7     -> ("Bb", "7")
    """
    chord = str(chord)
    if len(chord) >= 2 and chord[1] in ["#", "b"]:
        root = chord[:2]
        specification = chord[2:]
    else:
        root = chord[0]
        specification = chord[1:]

    return root, specification


def chord_degrees(
    key: str, chords: Iterable[Mapping[str, object]]
) -> Iterator[str | None]:
    """Yield one Roman numeral per input chord, preserving its position."""
    key = enharmonic_to_sharp(key)
    key_root, key_spec = split_chord(key)
    key_index = SEMIS.index(key_root)

    if key_spec == "m":
        chromatic_degrees = CHROMATIC_DEGREES_MINOR
        natural_specifications = NATURAL_SPECIFICATIONS_MINOR
    else:
        chromatic_degrees = CHROMATIC_DEGREES_MAJOR
        natural_specifications = NATURAL_SPECIFICATIONS_MAJOR

    for chord_info in chords:
        # Normalize both chord labels and chord objects supplied by callers.
        chord = str(chord_info["chord"])
        root, specification = split_chord(chord)
        root = enharmonic_to_sharp(root)

        try:
            chord_index = SEMIS.index(root)
        except ValueError:
            yield None
            continue

        interval = (chord_index - key_index) % 12

        degree = chromatic_degrees[interval]
        if key_spec == "m" and interval == 7 and specification in {"", "7"}:
            yield "V" + specification
            continue

        # Adding specification if it differs from the natural one of the key
        # (e.g., "Am" in the key of C major is VI, but "Gm" would be Vm)
        if interval in natural_specifications:
            expected = natural_specifications[interval]

            if specification != expected:
                if specification:
                    degree += specification
        else:
            if specification:
                degree += specification

        yield degree


def chords_to_degree_events(
    key: str | None, chords: Iterable[Mapping[str, object]]
) -> list[tuple[str, str]]:
    if key is None:
        return []
    chord_list = list(chords)
    return [
        (degree, str(chord["chord"]))
        for chord, degree in zip(chord_list, chord_degrees(key, chord_list))
        if degree is not None
    ]


def chords_to_degrees(
    key: str | None, chords: Iterable[Mapping[str, object]]
) -> list[str]:
    """Degrés seuls (sans les accords). Voir ``chords_to_degree_events``."""
    return [degree for degree, _ in chords_to_degree_events(key, chords)]


def degrees_to_chords(key: str | None, degrees: Sequence[str]) -> list[str]:
    """Inverse de ``chords_to_degrees`` : transforme des degrés en noms d'accords.

    Un degré est un degré chromatique éventuellement suivi de spécifications
    (ex. ``"vi"``, ``"Imaj7"``, ``"vii°"``, ``"Vadd4"``). S'il n'y a pas de
    spécification explicite, on rétablit la qualité **naturelle** du degré dans
    la tonalité (``"vi"`` en Do majeur -> ``"Am"``, et non ``"A"``).
    """
    if not degrees:
        return []

    key = enharmonic_to_sharp(key)
    key_root, key_spec = split_chord(key)
    key_index = SEMIS.index(key_root)

    if key_spec == "m":
        chromatic_degrees = CHROMATIC_DEGREES_MINOR
        natural_specifications = NATURAL_SPECIFICATIONS_MINOR
    else:
        chromatic_degrees = CHROMATIC_DEGREES_MAJOR
        natural_specifications = NATURAL_SPECIFICATIONS_MAJOR

    # On teste les degrés du plus long au plus court pour que "#IV" soit reconnu
    # avant "I", et "vii°" avant "vi" (sinon le "°" serait pris pour une spec).
    degrees_by_length = sorted(chromatic_degrees, key=len, reverse=True)

    chords = []
    for degree in degrees:
        # The reference progressions use a major dominant in minor keys.
        if key_spec == "m" and degree in {"V", "V7"}:
            chords.append(SEMIS[(key_index + 7) % 12] + degree[1:])
            continue
        base = next((d for d in degrees_by_length if degree.startswith(d)), None)
        if base is None:
            print(f"Unknown degree : {degree}")
            continue

        specification = degree[len(base) :]
        interval = chromatic_degrees.index(base)

        # pas de spécification explicite -> on remet la qualité naturelle du degré
        if not specification:
            specification = natural_specifications.get(interval, "")

        root = SEMIS[(key_index + interval) % 12]
        chords.append(root + specification)

    return chords


def progression_simplification(
    progression: Sequence[str], *, collapse_repeats: bool = True
) -> list[str]:
    simplified_progression = list(progression)

    # removing extra specifications
    for i, chord in enumerate(simplified_progression):
        while any(chord.endswith(spec) for spec in SPECIFICATIONS) or "/" in chord:
            for spec in SPECIFICATIONS:
                if chord.endswith(spec):
                    chord = chord[: -len(spec)]
                    break
                if "/" in chord:
                    chord = chord.split("/")[0]
                    break
        simplified_progression[i] = chord

    if not collapse_repeats:
        return simplified_progression

    # removing consecutive identical chords
    simplified: list[str] = []
    for chord in simplified_progression:
        if not simplified or chord != simplified[-1]:
            simplified.append(chord)

    return simplified


def suggest_next_chord(
    key: str | None, chords: Iterable[Mapping[str, object]]
) -> tuple[list[str], list[str]]:
    degree_progression = chords_to_degrees(key, chords)
    mode: ProgressionMode | None = ("minor" if key.endswith("m") else "major") if key else None
    return degree_progression, [
        match.degree for match in rank_next_degrees(degree_progression, mode=mode)
    ]


def suggest_next_degrees(degree_progression: list[str]) -> list[str]:
    return [match.degree for match in rank_next_degrees(degree_progression)]


def reference_distance(observed: tuple[str, ...], prefix: tuple[str, ...]) -> int | None:
    # Anchor on the current harmony and prefer retaining the most recent approach.
    if len(observed) < 2 or observed[-1] != prefix[-1]:
        return None
    if len(observed) == 2:
        return 3 if observed == prefix[-2:] else None
    differences = (observed[0] != prefix[0], observed[1] != prefix[1])
    if all(differences):
        return None
    return int(differences[0]) + 2 * int(differences[1])


def rank_next_degrees(
    progression: Sequence[str],
    *,
    mode: ProgressionMode | None = None,
    earlier_degrees: Sequence[str] = (),
) -> list[RankedContinuation]:
    """Rank the confirmed ending, using degrees across a gap only as secondary evidence."""
    observed = progression_simplification(progression, collapse_repeats=False)
    earlier = set(progression_simplification(earlier_degrees))
    if not observed or (len(observed) < 2 and not earlier):
        return []
    contexts = {tuple(observed[-3:]), tuple(progression_simplification(observed)[-3:])}

    best_distance: int | None = None
    matches: dict[str, list[tuple[int, tuple[str, ...]]]] = {}
    for reference in load_reference_progressions():
        if len(reference.degrees) < 4 or (mode is not None and mode != reference.mode):
            continue
        prefix = tuple(progression_simplification(reference.degrees[:3], collapse_repeats=False))
        distances = [reference_distance(context, prefix) for context in contexts]
        distance = min((value for value in distances if value is not None), default=None)
        if distance is None:
            if not earlier or observed[-1] != prefix[-1]:
                continue
            distance = 4  # Same current chord, without a reliable match for its approach.
        if best_distance is not None and distance > best_distance:
            continue
        if best_distance is None or distance < best_distance:
            matches.clear()
            best_distance = distance
        support = len(earlier.intersection(prefix[:-1])) if distance else 0
        matches.setdefault(reference.degrees[3], []).append((support, reference.degrees))

    kinds: dict[int, MatchKind] = {0: "exact", 1: "similar", 2: "similar", 3: "short", 4: "gap"}
    if best_distance is None:
        return []
    ranked = []
    for degree, examples in matches.items():
        support, example = min(examples, key=lambda entry: (-entry[0], entry[1]))
        ranked.append(
            (support, RankedContinuation(degree, len(examples), example, kinds[best_distance]))
        )
    ranked.sort(key=lambda entry: (-entry[0], -entry[1].reference_matches, entry[1].degree))
    return [match for _, match in ranked]
