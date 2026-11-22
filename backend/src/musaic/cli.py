"""Command-line entry point (``musaic`` or ``python -m musaic``)."""

import argparse
from collections.abc import Sequence

from musaic.config import TEST_AUDIO_LONGER_PATH
from musaic.pipeline import RecordingAnalysis, analyze_recording
from musaic.rag.chat import LLMChat


def asking_rag(result: RecordingAnalysis) -> None:
    progression = ", ".join(
        f"{event.chord} ({event.degree})" if event.degree else event.chord or "unclear harmony"
        for event in result.progression
    )
    key = result.key or "undetermined"
    query = f"I played {progression}. The estimated key is {key}. "
    if result.key_status == "tentative":
        query += "The key estimate is tentative. "
    if result.suggestions:
        candidates = ", ".join(f"{event.chord} ({event.degree})" for event in result.suggestions)
        query += (
            f"The music engine suggests {candidates}. "
            "Explain the effect of each continuation and suggest relevant variations."
        )
    else:
        query += "Suggest suitable continuations and briefly explain the effect of each."

    LLMChat().start_chat(initial_query=query)


def main(argv: Sequence[str] | None = None) -> None:
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

    result = analyze_recording(args.audio)
    if not any(event.chord is not None for event in result.progression):
        print("No chords were detected in this recording.")
        return
    if result.key_status == "tentative":
        also_plausible = f" (also plausible: {result.alternative_key})" if result.alternative_key else ""
        print(f"Tentative key: {result.key}{also_plausible}")
    print("Detected chords:", ", ".join(event.chord or "unclear harmony" for event in result.progression))
    asking_rag(result)


if __name__ == "__main__":
    main()
