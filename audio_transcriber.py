from basic_pitch.inference import predict

from config import TEST_AUDIO_PATH


def transcribe_audio(audio_path):
    _, midi_data, _ = predict(audio_path)
    notes = []
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
