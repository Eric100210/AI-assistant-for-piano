"""Couche de service : transforme le cœur ``musaic`` en schémas d'API.

Les routes HTTP ne contiennent **aucune** logique métier : elles délèguent ici.
C'est le seul module qui connaît à la fois ``musaic`` et l'API.

👉 Trois fonctions contiennent un ``TODO (toi)`` : ``parse_key``,
``build_progression`` et ``make_standalone_query``. Les fonctions qui les
utilisent sont déjà branchées : dès que tu les implémentes, l'endpoint marche.
"""

import logging
from pathlib import Path
from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from musaic.api.schemas import Analysis, ChatMessage, ChordEvent, Suggestion
from musaic.audio.chord_detector import detect_chords
from musaic.audio.transcriber import transcribe_audio
from musaic.engine.musical_engine import detect_key_from_notes, suggest_next_chord
from musaic.rag.retrieval import generate_response, retrieve_documents

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
    # -------------------------------------------------------------------------
    # TODO (toi) — implémente cette fonction.
    #
    # Indices :
    #   * une tonalité mineure se termine par le caractère "m"
    #   * sinon, elle est majeure
    #   * la racine est la tonalité sans le "m" final
    #   * renvoie un tuple : (racine, "majeur" ou "mineur")
    #
    # N'oublie pas de remplacer le `raise` ci-dessous par ton `return`.
    # -------------------------------------------------------------------------
    raise NotImplementedError("TODO: implémente parse_key() dans services.py")


def build_progression(degrees: list[str], chords: list[dict]) -> list[ChordEvent]:
    """Associe chaque degré à son nom d'accord.

    ``degrees`` provient de ``suggest_next_chord`` (ex. ``["I", "vi", "IV"]``) et
    ``chords`` de ``detect_chords`` (ex. ``[{"chord": "C"}, {"chord": "Am"}, ...]``).
    Les deux décrivent la même progression, dans le même ordre.

    Résultat attendu :
        [ChordEvent(degree="I",  chord="C"),
         ChordEvent(degree="vi", chord="Am"),
         ChordEvent(degree="IV", chord="F")]
    """
    # -------------------------------------------------------------------------
    # TODO (toi) — implémente cette fonction.
    #
    # Indices :
    #   * parcours les degrés avec leur index : `for i, degree in enumerate(degrees)`
    #   * le nom d'accord correspondant est dans `chords[i]["chord"]`
    #   * construis un ChordEvent(degree=..., chord=...)
    #   * renvoie la liste des ChordEvent
    #
    # Attention : `degrees` peut être légèrement plus courte que `chords`
    # (le moteur ignore les accords qu'il ne sait pas convertir en degré).
    # Utilise la liste la plus courte pour éviter un IndexError, ou prévois
    # une corde de secours : `chords[i]["chord"] if i < len(chords) else ""`.
    # -------------------------------------------------------------------------
    raise NotImplementedError("TODO: implémente build_progression() dans services.py")


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

    midi_notes = transcribe_audio(str(audio_path))
    pitches = [note["pitch"] for note in midi_notes]

    key = detect_key_from_notes(pitches)
    chords = detect_chords(midi_notes)
    degrees, next_chord = suggest_next_chord(key, chords)

    key_root, key_mode = parse_key(key)
    progression = build_progression(degrees, chords)
    confidence = estimate_confidence(key, degrees)

    candidates = [ChordEvent(degree=next_chord, chord="")] if next_chord else []

    return Analysis(
        fileName=file_name,
        durationLabel=duration_label,
        keyRoot=key_root,
        keyMode=key_mode,
        confidence=confidence,
        progression=progression,
        suggestion=Suggestion(
            candidates=candidates,
            rationale="Suggestion issue du moteur musical déterministe.",
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


def make_standalone_query(query: str, history: list[BaseMessage]) -> str:
    """Reformule la question pour qu'elle soit compréhensible sans contexte."""
    # -------------------------------------------------------------------------
    # TODO (toi) — rends la question autonome quand il y a un historique.
    #
    # Inspecte ``musaic/rag/chat.py`` : la classe ``LLMChat`` fait déjà cela
    # dans sa méthode ``ask_question`` (elle demande au LLM de reformuler).
    # Reproduis la même idée ici, SANS la boucle interactive :
    #   * si ``history`` est vide  -> renvoie ``query`` tel quel
    #   * sinon -> construis une liste de messages (un SystemMessage qui
    #     demande de reformuler + l'historique + un HumanMessage avec la
    #     nouvelle question), appelle ``get_llm().invoke(...)`` et renvoie
    #     le texte obtenu
    #
    # En attendant, renvoyer la question brute fonctionne (sans reformulation).
    # -------------------------------------------------------------------------
    return query


def answer_question(query: str, history: list[BaseMessage]) -> str:
    """Pipeline RAG complet, sans boucle interactive ni ``print``."""
    standalone_query = make_standalone_query(query, history)
    documents = retrieve_documents(standalone_query)
    return generate_response(standalone_query, documents)
