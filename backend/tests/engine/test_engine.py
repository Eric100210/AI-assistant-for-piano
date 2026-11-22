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
    def test_detect_key_from_notes(self, notes: list[int], expected_key: str) -> None:
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
    def test_split_chord(self, chord: str, expected: tuple[str, str]) -> None:
        assert split_chord(chord) == expected

    def test_chords_to_degrees(self) -> None:
        major_chords = [{"chord": chord} for chord in ["C", "Am", "F", "G"]]
        assert chords_to_degrees("C", major_chords) == ["I", "vi", "IV", "V"]

        minor_chords = [{"chord": chord} for chord in ["Am", "C", "F", "G"]]
        assert chords_to_degrees("Am", minor_chords) == ["i", "III", "VI", "VII"]

    def test_chords_to_degree_events_alignment(self) -> None:
        # chaque degré reste collé à SON accord, même si un accord est ignoré
        chords = [{"chord": "C"}, {"chord": "Xyz"}, {"chord": "F"}]
        assert chords_to_degree_events("C", chords) == [("I", "C"), ("IV", "F")]

    def test_chords_to_degree_events_accepts_chord_objects(self) -> None:
        # detect_chords renvoie des objets pychord.Chord : le moteur doit les
        # ramener à des chaînes (sinon l'API échoue à sérialiser).
        from pychord import Chord

        chords = [{"chord": Chord("Cm")}, {"chord": Chord("F")}]
        assert chords_to_degree_events("C", chords) == [("Im", "Cm"), ("IV", "F")]

    def test_degrees_to_chords(self) -> None:
        degrees = ["I", "vi", "IV", "V"]
        assert degrees_to_chords("C", degrees) == ["C", "Am", "F", "G"]

        degrees = ["i", "III", "VI", "VII"]
        assert degrees_to_chords("Am", degrees) == ["Am", "C", "F", "G"]

    def test_degrees_to_chords_round_trip(self) -> None:
        # accord -> degré -> accord doit redonner la progression de départ
        chords = [{"chord": chord} for chord in ["C", "Am", "F", "G"]]
        degrees = chords_to_degrees("C", chords)
        assert degrees_to_chords("C", degrees) == ["C", "Am", "F", "G"]

    def test_degrees_to_chords_with_specifications(self) -> None:
        # les spécifications explicites sont conservées, dans le bon ordre
        assert degrees_to_chords("C", ["Imaj7", "V7", "vi"]) == ["Cmaj7", "G7", "Am"]
        # les degrés "naturels" reprennent leur qualité, majeur comme mineur
        assert degrees_to_chords("C", ["ii", "vii°"]) == ["Dm", "Bdim"]
        assert degrees_to_chords("Am", ["i", "v"]) == ["Am", "Em"]

    def test_suggest_next_chord_returns_a_list(self) -> None:
        chords = [{"chord": chord} for chord in ["C", "Am", "F"]]
        degrees, next_degrees = suggest_next_chord("C", chords)
        assert degrees == ["I", "vi", "IV"]
        # renvoyé sous forme de liste, déjà prêt à contenir une suite d'accords
        assert next_degrees == ["V"]

    def test_suggest_next_chord_without_match(self) -> None:
        chords = [{"chord": "C"}]
        _, next_degrees = suggest_next_chord("C", chords)
        assert next_degrees == []

    def test_progression_simplification(self) -> None:
        # specifications removed and consecutive duplicates collapsed
        assert progression_simplification(["Imaj7", "V7", "V7", "vi"]) == [
            "I",
            "V",
            "vi",
        ]
        # inversions removed
        assert progression_simplification(["C/G", "F"]) == ["C", "F"]

    def test_suggest_next_chord_without_detected_chords(self) -> None:
        assert suggest_next_chord("C", []) == ([], [])
        assert detect_key_from_notes([]) is None

    def test_major_dominant_suggestion_in_minor(self) -> None:
        chords = [{"chord": chord} for chord in ["Am", "F", "Dm"]]
        _, next_degrees = suggest_next_chord("Am", chords)
        assert next_degrees == ["V"]
        assert degrees_to_chords("Am", next_degrees) == ["E"]

    def test_ranks_all_reference_continuations(self) -> None:
        from musaic.engine.musical_engine import rank_next_degrees

        matches = rank_next_degrees(["I", "V", "vi"])
        assert [(match.degree, match.reference_matches) for match in matches] == [
            ("IV", 1),
            ("V", 1),
        ]
        assert matches[0].example == ("I", "V", "vi", "IV")
        assert rank_next_degrees(["I", "vi", "IV"])[0].reference_matches == 2
        assert [match.degree for match in rank_next_degrees(["i", "i", "VI"])] == ["V", "VI"]

    def test_reference_count_precedes_tie_break(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from musaic.engine import musical_engine

        references = (
            musical_engine.ReferenceProgression(("I", "V", "vi", "IV"), "major"),
            musical_engine.ReferenceProgression(("I", "V", "vi", "V"), "major"),
            musical_engine.ReferenceProgression(("I", "V", "vi", "V"), "major"),
        )
        monkeypatch.setattr(musical_engine, "load_reference_progressions", lambda: references)
        assert musical_engine.suggest_next_degrees(["I", "V", "vi"]) == ["V", "IV"]

    def test_key_estimate_surfaces_ambiguity(self) -> None:
        from musaic.engine.musical_engine import estimate_key

        assert estimate_key([]).status == "undetermined"
        assert estimate_key([60]).status == "tentative"
        assert estimate_key(C_MAJOR_I_VI_IV_V).status == "estimated"
        estimate = estimate_key([60, 62, 64, 65, 67, 69, 71])
        assert (estimate.key, estimate.status, estimate.alternative) == ("C", "tentative", "Am")

    def test_similar_progression_preserves_the_recent_approach(self) -> None:
        from musaic.engine.musical_engine import rank_next_degrees

        matches = rank_next_degrees(["iii", "vi", "IV"], mode="major")
        assert [(match.degree, match.reference_matches, match.match_kind) for match in matches] == [
            ("V", 2, "similar")
        ]
        assert matches[0].example == ("I", "vi", "IV", "V")

    def test_exact_match_wins_over_more_frequent_neighbours(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from musaic.engine import musical_engine

        exact = musical_engine.ReferenceProgression(("I", "V", "vi", "IV"), "major")
        neighbour = musical_engine.ReferenceProgression(("IV", "V", "vi", "V"), "major")
        other_mode = musical_engine.ReferenceProgression(("I", "V", "vi", "V"), "minor")
        monkeypatch.setattr(
            musical_engine,
            "load_reference_progressions",
            lambda: (neighbour, neighbour, exact, other_mode),
        )
        matches = musical_engine.rank_next_degrees(["I", "V", "vi"], mode="major")
        assert [(match.degree, match.match_kind) for match in matches] == [("IV", "exact")]

    def test_short_context_and_rejecting_weak_matches(self) -> None:
        from musaic.engine.musical_engine import rank_next_degrees

        matches = rank_next_degrees(["I", "IV"], mode="major")
        assert [(match.degree, match.match_kind) for match in matches] == [("V", "short")]
        assert rank_next_degrees(["I", "IV"], mode="minor") == []
        assert rank_next_degrees(["bII", "bIII", "IV"], mode="major") == []
        assert rank_next_degrees(["I", "V", "#IV"], mode="major") == []

    def test_earlier_degrees_do_not_override_a_match_after_the_gap(self) -> None:
        from musaic.engine.musical_engine import rank_next_degrees

        matches = rank_next_degrees(["vi", "IV"], mode="major", earlier_degrees=["ii", "I"])
        assert [(match.degree, match.match_kind) for match in matches] == [("V", "short")]

        assert rank_next_degrees([], mode="minor", earlier_degrees=["i", "iv", "i"]) == []
        assert rank_next_degrees(["III", "i"], mode="minor") == []
