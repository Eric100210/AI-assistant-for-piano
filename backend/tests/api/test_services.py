"""Tests de la couche de service (adaptation cœur -> schémas d'API).

Ils ne lancent pas l'application FastAPI : on teste directement les fonctions
pures de ``musaic.api.services``.
"""

from musaic.api.services import build_progression, parse_key


def test_parse_key():
    assert parse_key("C") == ("C", "majeur")
    assert parse_key("F#") == ("F#", "majeur")
    assert parse_key("Am") == ("A", "mineur")
    assert parse_key("Cm") == ("C", "mineur")


def test_build_progression_converts_engine_events():
    events = [("I", "C"), ("vi", "Am"), ("IV", "F")]
    progression = build_progression(events)
    assert [(event.degree, event.chord) for event in progression] == [
        ("I", "C"),
        ("vi", "Am"),
        ("IV", "F"),
    ]


def test_build_progression_with_empty_events():
    assert build_progression([]) == []
