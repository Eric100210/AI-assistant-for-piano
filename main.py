# File with the main functions for the final application

from audio_transcriber import transcribe_audio
from chord_detector import (
    detect_key_from_notes,
    group_simultaneous_notes,
    detect_chords,
)
from musical_engine.musical_engine import suggest_next_chord


def suggest_next_chord_from_audio(audio_path):
    notes = transcribe_audio(audio_path)
    key = detect_key_from_notes(notes)
    simultaneous_notes = group_simultaneous_notes(notes)
    chords = detect_chords(simultaneous_notes)
    next_chord = suggest_next_chord(key, chords)
    return key, chords, next_chord
