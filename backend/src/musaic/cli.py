"""Command-line entry point (``musaic`` or ``python -m musaic``)."""

import argparse
from collections.abc import Sequence

from musaic.config import TEST_AUDIO_LONGER_PATH
from musaic.pipeline import RecordingAnalysis, analyze_recording
from musaic.rag.chat import LLMChat
from musaic.rag.retrieval import RecordingContext


def asking_rag(result: RecordingAnalysis) -> None:
    progression = ", ".join(
        f"{event.chord} ({event.degree})" if event.degree else event.chord or "unclear harmony"
        for event in result.progression
    )
    key = result.key or "undetermined"
    summary = f"I played {progression}. The estimated key is {key}."
    if result.key_status == "tentative":
        summary += " The key estimate is tentative."
    if result.suggestions:
        candidates = ", ".join(f"{event.chord} ({event.degree})" for event in result.suggestions)
        summary += f" The music engine suggests {candidates}."
        if result.suggestions[0].match_kind != "exact":
            summary += " These suggestions come from similar reference progressions."
        query = "Explain the effect of each suggested continuation and offer a playable variation."
    else:
        query = "Suggest a continuation I can play and briefly explain its effect."

    LLMChat().start_chat(
        initial_query=query,
        context=RecordingContext(
            summary=summary,
            key_mode=("minor" if result.key.endswith("m") else "major") if result.key else None,
            key_root=result.key.removesuffix("m") if result.key else None,
            dominant_reference_id=next(
                (event.reference_id for event in result.suggestions
                 if event.degree == "V" and event.reference_id is not None),
                None,
            ),
            reference_ids=tuple(
                event.reference_id for event in result.suggestions if event.reference_id is not None
            ),
        ),
    )


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
