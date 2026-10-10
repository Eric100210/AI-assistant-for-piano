import json
import os
import numpy as np

SEMIS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
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


def detect_key_from_notes(midi_notes):
    """
    Krumhansl-Schmuckler algorithm to determine the key and the mode
    Returns the key (C), the mode (major/minor), and the correlation score
    """

    pitch_classes = [note % 12 for note in midi_notes]
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


def chords_to_degrees(key, chords):

    key = enharmonic_to_sharp(key)
    key_root, key_spec = split_chord(key)
    key_index = SEMIS.index(key_root)

    if key_spec == "m":
        chromatic_degrees = CHROMATIC_DEGREES_MINOR
        natural_specifications = {
            0: "m",  # i
            2: "dim",  # ii°
            3: "",  # III
            5: "m",  # iv
            7: "m",  # v
            8: "",  # VI
            10: "",  # VII
        }

    else:
        chromatic_degrees = CHROMATIC_DEGREES_MAJOR
        natural_specifications = {
            0: "",  # I
            2: "m",  # ii
            4: "m",  # iii
            5: "",  # IV
            7: "",  # V
            9: "m",  # vi
            11: "dim",  # vii°
        }

    degrees = []

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

        degrees.append(degree)

    return degrees


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

    # for now, suggestion when perfect match, otherwise None
    # TODO : implement a more flexible suggestion system, e.g., using Levenshtein distance ?
    if last_three_degrees in reference_prog_cut:
        index = reference_prog_cut.index(last_three_degrees)
        next_prog = reference_prog[index]
        if len(next_prog) > 3:
            next_chord = next_prog[3]
            return degree_progression, next_chord
    return degree_progression, None


if __name__ == "__main__":
    print(reference_prog_cut)
    test_progression = ["Cm", "Gm", "Bm"]
    degree_progression, next_chord = suggest_next_chord("Cm", test_progression)
    print(f"Next chord suggestion for {test_progression}: {next_chord}")
