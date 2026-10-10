import os
import numpy as np
from pychord import find_chords_from_notes

from audio_transcriber import transcribe_audio

ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(ROOT, "test_data")
TEST_AUDIO_PATH = os.path.join(TEST_FOLDER, "test_audio_longer.mp3")

NOTE_THRESHOLD = 0.4  # threshold for considering a note as present in the window


SEMIS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHORD_TEMPLATES = {
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "diminished": (0, 3, 6),
    "augmented": (0, 4, 8),
    "major7": (0, 4, 7, 11),
    "minor7": (0, 3, 7, 10),
    "dominant7": (0, 4, 7, 10),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
}


def group_simultaneous_notes(notes, tolerance=0.03):
    groups = []

    for note in sorted(notes, key=lambda n: n["start"]):
        if not groups or note["start"] - groups[-1]["start"] > tolerance:
            groups.append({"start": note["start"], "notes": [note]})
        else:
            groups[-1]["notes"].append(note)

    return groups


def get_window_notes(notes, t, window_size=0.4, threshold=NOTE_THRESHOLD):
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

    selected_notes = [SEMIS[i] for i, score in enumerate(scores) if score >= threshold]
    return selected_notes, scores


def group_notes_by_time(notes, frequency=0.1):
    grouped_notes = []
    for t in np.arange(0, max(note["end"] for note in notes), frequency):
        window_notes, _ = get_window_notes(notes, t)
        if window_notes:
            grouped_notes.append({"time": t, "notes": window_notes})

    return grouped_notes


def detect_chord_from_notes(notes):
    if len(notes) < 3:
        return None

    pychord = find_chords_from_notes(notes)
    if pychord:
        return pychord[0]
    return None


def detect_chords_by_time(grouped_notes):
    chords = []
    for group in grouped_notes:
        chords.append(
            {"time": group["time"], "chord": detect_chord_from_notes(group["notes"])}
        )

    return chords


def merge_chords(chords):
    segments = []
    for chord_info in chords:
        chord = chord_info["chord"]
        time = chord_info["time"]

        if chord is None:
            continue

        if segments and segments[-1]["chord"] == chord:
            segments[-1]["end"] = time + 0.1
        else:
            segments.append({"chord": chord, "start": time, "end": time + 0.1})

    return segments


def detect_chords(notes):
    grouped_notes = group_notes_by_time(notes)
    chords = detect_chords_by_time(grouped_notes)
    merged_chords = merge_chords(chords)
    return merged_chords


def _manual_detect_chord(pitches):
    """not used anymore"""
    pitch_classes = {pitch % 12 for pitch in pitches}

    if len(pitch_classes) < 2:  # not a real chord
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


def _manual_detect_chords(notes_list: list[dict]):
    """not used anymore"""
    if not notes_list:
        return None
    chords = []
    for group in notes_list:
        pitches = [note["pitch"] for note in group["notes"]]
        chord = _manual_detect_chord(pitches)
        if chord:
            chords.append(chord)

    return chords


if __name__ == "__main__":
    notes = transcribe_audio(TEST_AUDIO_PATH)

    print("\nNotes détectées :")
    for note in notes:
        print(
            f"Note {SEMIS[note['pitch'] % 12]} {note['pitch']} | {note['start']:.2f}s - {note['end']:.2f}s"
        )

    notes_by_time = group_notes_by_time(notes)
    print("\nNotes regroupées par fenêtre temporelle :")
    for i, group in enumerate(notes_by_time):
        print(f"Fenêtre {i + 1} (temps {group['time']:.2f}s) :")
        for note in group["notes"]:
            print(note)

    chords_by_time = detect_chords_by_time(notes_by_time)
    merged_chords = merge_chords(chords_by_time)
    print("\nAccords détectés :")
    for i, chord in enumerate(merged_chords):
        print(
            f"Accord {i + 1} ({chord['chord']}) : {chord['start']:.2f}s - {chord['end']:.2f}s"
        )
