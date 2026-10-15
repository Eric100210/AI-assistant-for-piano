"""Couche de service : transforme le cœur ``musaic`` en schémas d'API.

Les routes HTTP ne contiennent **aucune** logique métier : elles délèguent ici.
C'est le seul module qui connaît à la fois ``musaic`` et l'API.
"""

import logging
from pathlib import Path
from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from musaic.api.schemas import Analysis, ChatMessage, ChordEvent, Suggestion
from musaic.audio.chord_detector import detect_chords
from musaic.audio.transcriber import transcribe_audio
from musaic.engine.musical_engine import (
    chords_to_degree_events,
    degrees_to_chords,
    detect_key_from_notes,
    suggest_next_chord,
)
from musaic.rag.retrieval import (
    generate_response,
    retrieve_documents,
    make_standalone_query,
)

logger = logging.getLogger(__name__)


# =============================================================================
#  Analyse audio                (branche sur POST /api/analyze)
# =============================================================================


def parse_key(key: str) -> tuple[str, Literal["majeur", "mineur"]]:
    """Découpe la tonalité renvoyée par le moteur en ``(racine, mode)``.

    Le moteur renvoie par exemple ``"C"`` (majeur) ou ``"Am"`` (mineur) : le
    mode mineur est signalé par un ``"m"`` final.

    Exemples attendus :
        "C"  -> ("C",  "majeur")
        "F#" -> ("F#", "majeur")
        "Am" -> ("A",  "mineur")
        "Cm" -> ("C",  "mineur")
    """
    if key.endswith("m"):
        return key[:-1], "mineur"
    return key, "majeur"


def build_progression(events: list[tuple[str, str]]) -> list[ChordEvent]:
    """Convertit des paires ``(degré, accord)`` du moteur en ``ChordEvent``.

    ``events`` provient de ``chords_to_degree_events`` : chaque degré y est déjà
    associé à SON accord d'origine (les accords non reconnus ont été retirés à la
    source), donc aucun risque de décalage.

    Exemple :
        [("I", "C"), ("vi", "Am"), ("IV", "F")]
        -> [ChordEvent(degree="I",  chord="C"),
            ChordEvent(degree="vi", chord="Am"),
            ChordEvent(degree="IV", chord="F")]
    """
    return [ChordEvent(degree=degree, chord=chord) for degree, chord in events]


def estimate_confidence(key: str, degrees: list[str]) -> float:
    """Indice de confiance (0 → 1) de l'analyse.

    Pour l'instant : valeur neutre, pour ne pas bloquer l'endpoint.
    """
    # -------------------------------------------------------------------------
    # TODO (toi, plus tard) — améliore cette estimation.
    #
    # Piste : ``detect_key_from_notes`` (dans musaic/engine/musical_engine.py)
    # calcule déjà un score de corrélation, mais ne le renvoie pas. Tu pourras
    # le faire remonter (par ex. renvoyer un tuple ``(key, score)``) puis
    # l'utiliser ici, sans casser le CLI.
    # -------------------------------------------------------------------------
    return 0.0


def analyze_audio(
    audio_path: Path, file_name: str, duration_label: str = "—"
) -> Analysis:
    """Orchestration complète : fichier audio -> ``Analysis``.

    Reprend les étapes de ``musaic.pipeline.suggest_next_chord_from_audio``,
    mais conserve aussi les **noms d'accords** détectés (que le pipeline
    historique jette), dont le front a besoin.
    """
    logger.info("Analyse audio de %s", audio_path)

    midi_notes = transcribe_audio(str(audio_path))  # list[dict]
    pitches = [note["pitch"] for note in midi_notes]  # list[int]

    key = detect_key_from_notes(pitches)
    chords = detect_chords(midi_notes)  # list[dict{chord, start, end}]
    progression = build_progression(chords_to_degree_events(key, chords))

    # vraie progression en degrés + suite de degrés suggérée par le moteur
    degrees, next_degrees = suggest_next_chord(key, chords)

    key_root, key_mode = parse_key(key)

    # le moteur raisonne en degrés : on les retransforme en vrais noms d'accords
    next_chords = degrees_to_chords(key, next_degrees)
    candidates = [
        ChordEvent(degree=degree, chord=chord)
        for degree, chord in zip(next_degrees, next_chords)
    ]
    if candidates:
        rationale = "Suggestion issue du moteur musical déterministe."
    else:
        rationale = "Vous pouvez demander à l'assistant MusAIc de vous aider sur cette progression."

    # plutôt passer le score de corrélation de detect_key_from_notes(), potentiellement aussi un indicateur qui vient du suggest_next_chord amélioré
    confidence = estimate_confidence(key, degrees)

    return Analysis(
        fileName=file_name,
        durationLabel=duration_label,
        keyRoot=key_root,
        keyMode=key_mode,
        confidence=confidence,
        progression=progression,
        suggestion=Suggestion(
            candidates=candidates,
            rationale=rationale,
        ),
    )


# =============================================================================
#  Chat RAG                     (branche sur POST /api/chat)
# =============================================================================


def build_history_messages(history: list[ChatMessage]) -> list[BaseMessage]:
    """Convertit l'historique (contrat API) en messages LangChain.

    Le front envoie l'historique à chaque requête : l'API reste sans état.
    """
    messages: list[BaseMessage] = []
    for message in history:
        if message.role == "user":
            messages.append(HumanMessage(content=message.content))
        else:
            messages.append(AIMessage(content=message.content))
    return messages


def answer_question(query: str, history: list[BaseMessage]) -> str:
    """Pipeline RAG complet, sans boucle interactive ni ``print``."""
    standalone_query = make_standalone_query(query, history)
    documents = retrieve_documents(standalone_query)
    return generate_response(standalone_query, documents)
