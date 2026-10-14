"""Application pipeline: from an audio file to a chord suggestion."""

from musaic.audio.chord_detector import detect_chords
from musaic.audio.transcriber import transcribe_audio
from musaic.engine.musical_engine import detect_key_from_notes, suggest_next_chord


def suggest_next_chord_from_audio(audio_path):
    midi_notes = transcribe_audio(audio_path)  # list[dict{pitch, start, end, velocity}]
    notes = [note["pitch"] for note in midi_notes]
    key = detect_key_from_notes(notes)  # str with key + mode
    chords = detect_chords(midi_notes)  # list[dict{chord, start, end}]
    progression_degrees, next_chord = suggest_next_chord(key, chords)
    return key, progression_degrees, next_chord  # for the RAG query
