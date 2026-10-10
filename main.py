# File with the main functions for the final application
import os

from audio_transcriber import transcribe_audio
from chord_detector import (
    detect_chords,
)
from musical_engine.musical_engine import detect_key_from_notes, suggest_next_chord

# Test data
ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(ROOT, "test_data")
TEST_AUDIO_PATH = os.path.join(TEST_FOLDER, "test_audio_longer.mp3")


def suggest_next_chord_from_audio(audio_path):
    midi_notes = transcribe_audio(audio_path)  # list[dict{pitch, start, end, velocity}]
    for note in midi_notes:
        print(
            f"Pitch: {note['pitch']}, Start: {note['start']:.2f}, End: {note['end']:.2f}, Velocity: {note['velocity']}"
        )
    notes = [note["pitch"] for note in midi_notes]
    key = detect_key_from_notes(notes)  # str with key+tone
    chords = detect_chords(midi_notes)  # list[dict[chord, start, end]]
    next_chord = suggest_next_chord(key, chords)
    return key, chords, next_chord  # for the RAG query


if __name__ == "__main__":
    key, chords, next_chord = suggest_next_chord_from_audio(TEST_AUDIO_PATH)
    print(f"Key: {key}")
    print(f"Chords: {chords}")
    print(f"Suggested next chord: {next_chord}")
