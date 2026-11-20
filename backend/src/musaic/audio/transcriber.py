from pathlib import Path
from typing import TypedDict

from basic_pitch.inference import predict


class MidiNote(TypedDict):
    pitch: int
    start: float
    end: float


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
                }
            )
    return sorted(notes, key=lambda n: n["start"])
