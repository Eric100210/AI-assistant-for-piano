from pathlib import Path
from typing import TypedDict

from basic_pitch.inference import predict

from musaic.config import TEST_AUDIO_PATH


class MidiNote(TypedDict):
    pitch: int
    start: float
    end: float
    velocity: int


def transcribe_audio(audio_path: str | Path) -> list[MidiNote]:
    _, midi_data, _ = predict(audio_path)
    notes: list[MidiNote] = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            notes.append(
                {
                    "pitch": note.pitch,
                    "start": note.start,
                    "end": note.end,
                    "velocity": note.velocity,
                }
            )
    return sorted(notes, key=lambda n: n["start"])


if __name__ == "__main__":
    notes = transcribe_audio(TEST_AUDIO_PATH)
    for note in notes:
        print(
            f"Pitch: {note['pitch']}, Start: {note['start']:.2f}, End: {note['end']:.2f}, Velocity: {note['velocity']}"
        )
