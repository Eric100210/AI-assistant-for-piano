import json
from functools import lru_cache

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


@lru_cache(maxsize=1)
def load_reference_progressions():
    """Load the reference progressions once (lazy: importing this module stays side-effect free)."""
    with open(PROGRESSIONS_JSON) as f:
        content = json.load(f)

    reference_prog = [record["metadata"].get("degres", []) for record in content]
    reference_prog_cut = [prog[:3] for prog in reference_prog]
    return reference_prog, reference_prog_cut


def detect_key_from_notes(pitches):
    """
    Krumhansl-Schmuckler algorithm to determine the key and the mode
    Returns the key (C) with the mode, and the correlation score
    """

    pitch_classes = [note % 12 for note in pitches]
    note_profile = np.zeros(12)

    for pitch_class in pitch_classes:
        note_profile[pitch_class] += 1

    best_key = None
    best_mode = None
    best_score = -np.inf

    for i, key in enumerate(SEMIS):
        # Rotate the reference profiles so that they correspond
        # to the current tonic
        major_profile = np.roll(MAJOR_PROFILE, i)
        minor_profile = np.roll(MINOR_PROFILE, i)

        # Compare the played notes with the reference profiles
        major_score = np.corrcoef(note_profile, major_profile)[0, 1]
        minor_score = np.corrcoef(note_profile, minor_profile)[0, 1]

        if major_score > best_score:
            best_score = major_score
            best_key = key
            best_mode = "major"

        if minor_score > best_score:
            best_score = minor_score
            best_key = key
            best_mode = "minor"

    if best_mode == "minor":
        best_key += "m"

    return best_key


def enharmonic_to_sharp(note):
    conversion = {
        "Db": "C#",
        "Eb": "D#",
        "Gb": "F#",
        "Ab": "G#",
        "Bb": "A#",
    }

    return conversion.get(note, note)


def split_chord(chord):
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


def chords_to_degree_events(key, chords):
    """Associe chaque accord reconnu à son degré : ``[(degree, chord), ...]``.

    Les accords non reconnus sont **ignorés**. On renvoie donc chaque degré collé
    à SON accord d'origine : indispensable pour afficher une progression
    « degré + accord » sans risque de décalage.
    """
    key = enharmonic_to_sharp(key)
    key_root, key_spec = split_chord(key)
    key_index = SEMIS.index(key_root)

    if key_spec == "m":
        chromatic_degrees = CHROMATIC_DEGREES_MINOR
        natural_specifications = NATURAL_SPECIFICATIONS_MINOR
    else:
        chromatic_degrees = CHROMATIC_DEGREES_MAJOR
        natural_specifications = NATURAL_SPECIFICATIONS_MAJOR

    events = []

    for chord_info in chords:
        chord = chord_info["chord"]
        root, specification = split_chord(chord)
        root = enharmonic_to_sharp(root)

        try:
            chord_index = SEMIS.index(root)
        except ValueError:
            print(f"Unknown chord : {chord}")
            continue

        interval = (chord_index - key_index) % 12

        degree = chromatic_degrees[interval]

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

        events.append((degree, chord))

    return events


def chords_to_degrees(key, chords):
    """Degrés seuls (sans les accords). Voir ``chords_to_degree_events``."""
    return [degree for degree, _ in chords_to_degree_events(key, chords)]


def degrees_to_chords(key, degrees):
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


def progression_simplification(progression):
    simplified_progression = progression.copy()

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

    # removing consecutive identical chords
    simplified = [simplified_progression[0]]
    for chord in simplified_progression[1:]:
        if chord != simplified[-1]:
            simplified.append(chord)

    return simplified


def suggest_next_chord(key, chords):
    # chord_progression is the full progression of chords played so far
    # hoping that the full progression will help identify the key to convert in degrees
    degree_progression = chords_to_degrees(key, chords)
    print(f"Degree progression: {degree_progression}")

    simplified_progression = progression_simplification(degree_progression)
    print(f"Simplified progression: {simplified_progression}")

    last_three_degrees = (
        simplified_progression[-3:]
        if len(simplified_progression) >= 3
        else simplified_progression
    )

    # for now, suggestion when perfect match, otherwise an empty list
    # TODO (toi) : implémenter un système de suggestion plus souple (ex. distance
    # de Levenshtein) et capable de proposer une vraie **suite** de plusieurs
    # accords. L'interface renvoie déjà une liste : elle est prête pour ça.
    reference_prog, reference_prog_cut = load_reference_progressions()

    if last_three_degrees in reference_prog_cut:
        index = reference_prog_cut.index(last_three_degrees)
        next_prog = reference_prog[index]
        # tout ce qui suit les 3 degrés reconnus (aujourd'hui un seul accord,
        # car les progressions de référence font 4 degrés, mais une liste déjà)
        return degree_progression, next_prog[3:]
    return degree_progression, []


if __name__ == "__main__":
    _, reference_prog_cut = load_reference_progressions()
    print(reference_prog_cut)
    test_progression = [{"chord": "C"}, {"chord": "G"}, {"chord": "F"}]
    degree_progression, next_degrees = suggest_next_chord("C", test_progression)
    print(
        f"Next chord suggestion for {test_progression}: {next_degrees}, knowing {degree_progression}"
    )
