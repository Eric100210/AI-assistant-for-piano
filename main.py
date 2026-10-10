# File with the main functions for the final application
import os

from audio_transcriber import transcribe_audio
from chord_detector import (
    detect_chords,
)
from musical_engine.musical_engine import detect_key_from_notes, suggest_next_chord
from llm_chat import LLMChat

# Test data
ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(ROOT, "test_data")
TEST_AUDIO_PATH = os.path.join(TEST_FOLDER, "test_audio_longer.mp3")


def suggest_next_chord_from_audio(audio_path):
    midi_notes = transcribe_audio(audio_path)  # list[dict{pitch, start, end, velocity}]
    notes = [note["pitch"] for note in midi_notes]
    key = detect_key_from_notes(notes)  # str with key+tone
    chords = detect_chords(midi_notes)  # list[dict[chord, start, end]]
    progression_degrees, next_chord = suggest_next_chord(key, chords)
    return key, progression_degrees, next_chord  # for the RAG query


def asking_rag(key, progression_degrees, next_chord):
    query = f"""J’ai joué une progression {", ".join(progression_degrees)} en tonalité de {key}. 
    En regardant globalement la progression, on me conseille de continuer avec un accord parmi les suivants : {next_chord}. 
    Explique l’effet créé par ces progressions possibles (ou propose des cohérentes s'il n'y en a pas) et propose des variantes pertinentes connaissant la vraie progression et ses spécifications.
    """

    chat = LLMChat()
    chat.start_chat(initial_query=query)


if __name__ == "__main__":
    key, progression_degrees, next_chord = suggest_next_chord_from_audio(
        TEST_AUDIO_PATH
    )
    print("Progression degrees: ", progression_degrees)
    asking_rag(key, progression_degrees, next_chord)
