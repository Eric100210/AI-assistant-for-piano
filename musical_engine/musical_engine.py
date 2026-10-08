import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "progressions.json")) as f:
    content = json.load(f)
    reference_prog = []
    for record in content:
        reference_prog.append(record["metadata"].get("degres", []))

reference_prog_cut = [prog[:3] for prog in reference_prog]


def chords_to_degrees(key, chords):
    pass


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
    print(reference_prog_cut)
    test_progression = ["C", "G", "Am"]
    next_chord = suggest_next_chord("C", test_progression)
    print(f"Next chord suggestion for {test_progression}: {next_chord}")
