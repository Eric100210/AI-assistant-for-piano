"""Command-line entry point (``musaic`` or ``python -m musaic``)."""

import argparse

from musaic.config import TEST_AUDIO_LONGER_PATH
from musaic.pipeline import suggest_next_chord_from_audio
from musaic.rag.chat import LLMChat


def asking_rag(key, progression_degrees, next_degrees):
    if next_degrees:
        query = f"""J’ai joué une progression {", ".join(progression_degrees)} en tonalité de {key}. 
        En regardant globalement la progression, on me conseille de continuer avec un accord parmi les suivants : {", ".join(next_degrees)}. 
        Explique l’effet créé par ces progressions possibles et propose des variantes pertinentes connaissant la vraie progression et ses spécifications.
        """
    else:
        query = f"""J’ai joué une progression {", ".join(progression_degrees)} en tonalité de {key}. 
        Compte tenu de tes connaissances et des documents pertinents, propose des accords qui pourraient suivre cette progression, explique rapidement l’effet créé par ces progressions possibles et propose des variantes pertinentes.
        """

    chat = LLMChat()
    chat.start_chat(initial_query=query)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="musaic",
        description="Analyse un fichier audio et propose la suite d'une progression d'accords.",
    )
    parser.add_argument(
        "audio",
        nargs="?",
        default=str(TEST_AUDIO_LONGER_PATH),
        help="Chemin du fichier audio à analyser (défaut : audio de test).",
    )
    args = parser.parse_args(argv)

    key, progression_degrees, next_degrees = suggest_next_chord_from_audio(args.audio)
    print("Progression degrees: ", progression_degrees)
    asking_rag(key, progression_degrees, next_degrees)


if __name__ == "__main__":
    main()
