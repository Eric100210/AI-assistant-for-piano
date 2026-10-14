import pytest

from musaic.engine.musical_engine import (
    chords_to_degrees,
    detect_key_from_notes,
    progression_simplification,
    split_chord,
)

MIDI_NOTES = [60, 64, 67]  # C major triad


class TestEngine:
    def test_detect_key_from_notes(self):
        assert detect_key_from_notes(MIDI_NOTES) == "C"

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

    def test_progression_simplification(self):
        # specifications removed and consecutive duplicates collapsed
        assert progression_simplification(["Imaj7", "V7", "V7", "vi"]) == [
            "I",
            "V",
            "vi",
        ]
        # inversions removed
        assert progression_simplification(["C/G", "F"]) == ["C", "F"]
