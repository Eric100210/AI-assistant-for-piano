from basic_pitch.inference import predict
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(ROOT, "test_data")
TEST_AUDIO_PATH = os.path.join(TEST_FOLDER, "test_audio.mp3")


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
