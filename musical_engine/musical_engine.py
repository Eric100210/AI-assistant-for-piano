import json
import os
import numpy as np

SEMIS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SPECIFICATIONS = ["m", "maj", "7", "6", "4", "9", "sus", "dim", "aug", "°"]
CHROMATIC_DEGREES = [
    "I",
    "bII",
    "II",
    "bIII",
    "III",
    "IV",
    "#IV",
    "V",
    "bVI",
    "VI",
    "bVII",
    "VII",
]

# Krumhansl-Kessler profiles
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)

MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "progressions.json")) as f:
    content = json.load(f)
    reference_prog = []
    for record in content:
        reference_prog.append(record["metadata"].get("degres", []))

reference_prog_cut = [prog[:3] for prog in reference_prog]


def krumhansl_schmuckler(note_profile):
    """
    Krumhansl-Schmuckler algorithm to determine the key and the mode
    Returns the key (C), the mode (major/minor), and the correlation score
    """

    note_profile = np.asarray(note_profile)

    if note_profile.shape != (12,):
        raise ValueError("note_profile doit contenir exactement 12 valeurs.")

    best_key = None
    best_mode = None
    best_score = -np.inf

    for i, key in enumerate(SEMIS):
        major_profile = np.roll(MAJOR_PROFILE, i)

        minor_profile = np.roll(MINOR_PROFILE, i)

        # Corrélation de Pearson
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

    return best_key, best_mode, best_score


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
    if len(chord) >= 2 and chord[1] in ["#", "b"]:
        root = chord[:2]
        specification = chord[2:]
    else:
        root = chord[0]
        specification = chord[1:]

    return root, specification


def chords_to_degrees(key, chords):

    # we use the sharp notation for the key
    key = enharmonic_to_sharp(key)
    key_root, key_spec = split_chord(key)
    key_index = SEMIS.index(key_root)

    degrees = []

    for chord in chords:
        root, specification = split_chord(chord)
        root = enharmonic_to_sharp(root)

        try:
            chord_index = SEMIS.index(root)
        except ValueError:
            print(f"Unknown chord : {chord}")
            continue

        interval = (chord_index - key_index) % 12

        degree = CHROMATIC_DEGREES[interval]
        if specification:
            if key_spec == "m":
                # if degree = I, IV or V, it is naturally minor in a minor key
                if not (specification == "m" and degree in ["I", "IV", "V"]):
                    degree += specification
            else:
                # if degree = II, III, VI or VII, it is naturally minor in a major key
                if not (specification == "m" and degree in ["II", "III", "VI", "VII"]):
                    degree += specification

        degrees.append(degree)

    return degrees


def suggest_next_chord(key, chords):
    # chord_progression is the full progression of chords played so far
    # hoping that the full progression will help identify the key to convert in degrees
    degree_progression = chords_to_degrees(key, chords)

    # Considering for now only the last 3 different chords
    last_three_degrees = degree_progression[-3:]
    if last_three_degrees in reference_prog_cut:
        index = reference_prog_cut.index(last_three_degrees)
        next_prog = reference_prog[index]
        return next_prog[3] if len(next_prog) > 3 else None
    return None


if __name__ == "__main__":
    # # chords_to_degrees test
    print(chords_to_degrees("C", ["C", "G", "Am"]))
    print(chords_to_degrees("Cm", ["Cm", "Gm", "B", "Eb"]))
    print(chords_to_degrees("Cm", ["Cm", "Gm", "Bm", "Eb"]))
    print(chords_to_degrees("Bb", ["Bb", "F", "Gm", "Eb"]))

    print(reference_prog_cut)
    test_progression = ["C", "G", "Am"]
    next_chord = suggest_next_chord("C", test_progression)
    print(f"Next chord suggestion for {test_progression}: {next_chord}")
