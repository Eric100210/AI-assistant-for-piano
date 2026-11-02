"""Command-line entry point (``musaic`` or ``python -m musaic``)."""

import argparse

from musaic.config import TEST_AUDIO_LONGER_PATH
from musaic.pipeline import suggest_next_chord_from_audio
from musaic.rag.chat import LLMChat


def asking_rag(key, progression_degrees, next_degrees):
    if next_degrees:
        query = (
            f"I played a progression {', '.join(progression_degrees)} in the key of {key}. "
            f"Looking at the progression as a whole, I'm advised to continue with one of the following chords: {', '.join(next_degrees)}. "
            "Explain the effect of each possible continuation and suggest relevant variations, taking the actual progression and its specifics into account."
        )
    else:
        query = (
            f"I played a progression {', '.join(progression_degrees)} in the key of {key}. "
            "Based on your knowledge and the relevant documents, suggest chords that could follow this progression. "
            "Briefly explain the effect of each possibility and suggest relevant variations."
        )

    chat = LLMChat()
    chat.start_chat(initial_query=query)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="musaic",
        description="Analyze an audio file and suggest the next chord in a progression.",
    )
    parser.add_argument(
        "audio",
        nargs="?",
        default=str(TEST_AUDIO_LONGER_PATH),
        help="Path to the audio file to analyze (default: test audio).",
    )
    args = parser.parse_args(argv)

    key, progression_degrees, next_degrees = suggest_next_chord_from_audio(args.audio)
    print("Progression degrees:", progression_degrees)
    asking_rag(key, progression_degrees, next_degrees)


if __name__ == "__main__":
    main()
