from pathlib import Path
from typing import TypedDict

from audioread import DecodeError
from basic_pitch.inference import predict
from soundfile import SoundFileError


class AudioDecodeError(ValueError):
    """The recording could not be decoded."""


class MidiNote(TypedDict):
    pitch: int
    start: float
    end: float


def transcribe_audio(audio_path: str | Path) -> list[MidiNote]:
    try:
        _, midi_data, _ = predict(audio_path)
    except (DecodeError, SoundFileError, EOFError) as error:
        raise AudioDecodeError("Could not decode this audio file.") from error
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
