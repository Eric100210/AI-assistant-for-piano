import pytest

from musaic.engine.musical_engine import (
    chords_to_degree_events,
    chords_to_degrees,
    degrees_to_chords,
    detect_key_from_notes,
    progression_simplification,
    split_chord,
    suggest_next_chord,
)

# Real progressions: chord tones played as a sequence (I - vi - IV - V).
C_MAJOR_I_VI_IV_V = [
    60,
    64,
    67,  # C
    57,
    60,
    64,  # Am
    53,
    57,
    60,  # F
    55,
    59,
    62,  # G
]
G_MAJOR_I_VI_IV_V = [
    55,
    59,
    62,  # G
    52,
    55,
    59,  # Em
    48,
    52,
    55,  # C
    50,
    54,
    57,  # D
]
F_MAJOR_I_VI_IV_V = [
    53,
    57,
    60,  # F
    50,
    53,
    57,  # Dm
    46,
    50,
    53,  # Bb
    48,
    52,
    55,  # C
]
A_MINOR_I_IV_V_I = [
    57,
    60,
    64,  # Am
    53,
    57,
    60,  # Dm
    52,
    56,
    59,  # E
    57,
    60,
    64,  # Am
]


class TestEngine:
    @pytest.mark.parametrize(
        "notes, expected_key",
        [
            (C_MAJOR_I_VI_IV_V, "C"),
            (G_MAJOR_I_VI_IV_V, "G"),
            (F_MAJOR_I_VI_IV_V, "F"),
            (A_MINOR_I_IV_V_I, "Am"),
        ],
    )
    def test_detect_key_from_notes(self, notes, expected_key):
        assert detect_key_from_notes(notes) == expected_key

    @pytest.mark.parametrize(
        "chord, expected",
        [
            ("C", ("C", "")),
            ("Am", ("A", "m")),
            ("Cmaj7", ("C", "maj7")),
            ("F#dim", ("F#", "dim")),
            ("Bb7", ("Bb", "7")),
        ],
    )
    def test_split_chord(self, chord, expected):
        assert split_chord(chord) == expected

    def test_chords_to_degrees(self):
        major_chords = [{"chord": chord} for chord in ["C", "Am", "F", "G"]]
        assert chords_to_degrees("C", major_chords) == ["I", "vi", "IV", "V"]

        minor_chords = [{"chord": chord} for chord in ["Am", "C", "F", "G"]]
        assert chords_to_degrees("Am", minor_chords) == ["i", "III", "VI", "VII"]

    def test_chords_to_degree_events_alignment(self):
        # chaque degré reste collé à SON accord, même si un accord est ignoré
        chords = [{"chord": "C"}, {"chord": "Xyz"}, {"chord": "F"}]
        assert chords_to_degree_events("C", chords) == [("I", "C"), ("IV", "F")]

    def test_degrees_to_chords(self):
        degrees = ["I", "vi", "IV", "V"]
        assert degrees_to_chords("C", degrees) == ["C", "Am", "F", "G"]

        degrees = ["i", "III", "VI", "VII"]
        assert degrees_to_chords("Am", degrees) == ["Am", "C", "F", "G"]

    def test_degrees_to_chords_round_trip(self):
        # accord -> degré -> accord doit redonner la progression de départ
        chords = [{"chord": chord} for chord in ["C", "Am", "F", "G"]]
        degrees = chords_to_degrees("C", chords)
        assert degrees_to_chords("C", degrees) == ["C", "Am", "F", "G"]

    def test_degrees_to_chords_with_specifications(self):
        # les spécifications explicites sont conservées, dans le bon ordre
        assert degrees_to_chords("C", ["Imaj7", "V7", "vi"]) == ["Cmaj7", "G7", "Am"]
        # les degrés "naturels" reprennent leur qualité, majeur comme mineur
        assert degrees_to_chords("C", ["ii", "vii°"]) == ["Dm", "Bdim"]
        assert degrees_to_chords("Am", ["i", "v"]) == ["Am", "Em"]

    def test_suggest_next_chord_returns_a_list(self):
        chords = [{"chord": chord} for chord in ["C", "Am", "F"]]
        degrees, next_degrees = suggest_next_chord("C", chords)
        assert degrees == ["I", "vi", "IV"]
        # renvoyé sous forme de liste, déjà prêt à contenir une suite d'accords
        assert next_degrees == ["V"]

    def test_suggest_next_chord_without_match(self):
        # moins de 3 degrés : impossible de matcher les progressions de référence
        chords = [{"chord": chord} for chord in ["C", "F"]]
        _, next_degrees = suggest_next_chord("C", chords)
        assert next_degrees == []

    def test_progression_simplification(self):
        # specifications removed and consecutive duplicates collapsed
        assert progression_simplification(["Imaj7", "V7", "V7", "vi"]) == [
            "I",
            "V",
            "vi",
        ]
        # inversions removed
        assert progression_simplification(["C/G", "F"]) == ["C", "F"]
