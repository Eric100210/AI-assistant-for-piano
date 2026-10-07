import pretty_midi
import os
import numpy as np

from audio_transcriber import transcribe_audio

ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(ROOT, "test_data")
TEST_AUDIO_PATH = os.path.join(TEST_FOLDER, "test_audio.mp3")


SEMIS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHORD_TEMPLATES = {
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "diminished": (0, 3, 6),
    "augmented": (0, 4, 8),
    "major7": (0, 4, 7, 11),
    "minor7": (0, 3, 7, 10),
    "dominant7": (0, 4, 7, 10),
}


def group_simultaneous_notes(notes, tolerance=0.03):
    groups = []

    for note in sorted(notes, key=lambda n: n["start"]):
        if not groups or note["start"] - groups[-1]["start"] > tolerance:
            groups.append({"start": note["start"], "notes": [note]})
        else:
            groups[-1]["notes"].append(note)

    return groups


def detect_chord(pitches):
    pitch_classes = {pitch % 12 for pitch in pitches}

    if len(pitch_classes) < 3:  # not a real chord
        return None

    best_chord = None
    best_score = float("-inf")

    for root in range(12):
        for chord_type, intervals in CHORD_TEMPLATES.items():
            expected = {(root + interval) % 12 for interval in intervals}

            # score to get the best corresponding chord
            matched = len(pitch_classes & expected)
            missing = len(expected - pitch_classes)
            extra = len(pitch_classes - expected)

            score = 2 * matched - missing - 1.5 * extra

            if score > best_score:
                best_score = score
                best_chord = f"{SEMIS[root]} {chord_type}"

    return best_chord


def detect_chords(notes_list):
    if not notes_list:
        return None

    groups = group_simultaneous_notes(notes)

    chords = []
    for group in groups:
        pitches = [note["pitch"] for note in group["notes"]]
        chord = detect_chord(pitches)
        if chord:
            chords.append(chord)

    return chords


def detect_chords_from_audio(audio_path):
    notes = transcribe_audio(audio_path)
    simultaneous_notes = group_simultaneous_notes(notes)
    chords = detect_chords(simultaneous_notes)
    return chords


if __name__ == "__main__":
    notes = transcribe_audio(TEST_AUDIO_PATH)

    print("\nNotes détectées :")
    for note in notes:
        print(f"Pitch MIDI {note['pitch']} | {note['start']:.2f}s - {note['end']:.2f}s")

    simultaneous_notes = group_simultaneous_notes(notes)
    print("\nNotes simultanées détectées :")
    for i, group in enumerate(simultaneous_notes):
        print(f"Groupe {i + 1} :")
        for note in group["notes"]:
            print(
                f"  - Pitch MIDI {note['pitch']} | {note['start']:.2f}s - {note['end']:.2f}s"
            )

    chords = detect_chords(simultaneous_notes)
    print("\nAccords détectés :")
    for i, chord in enumerate(chords):
        print(f"Accord {i + 1} : {chord}")
