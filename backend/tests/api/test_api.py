"""Tests de l'API FastAPI.

Ils utilisent le ``TestClient`` : l'application tourne en mémoire, sans lancer
uvicorn. Ils sont ignorés automatiquement si FastAPI n'est pas installé.
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from musaic.api.main import app  # noqa: E402

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_validates_request_body() -> None:
    # Un corps sans "query" doit être rejeté par Pydantic (422) avant
    # même d'atteindre la logique RAG (donc sans besoin d'Ollama).
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_analyze_rejects_unknown_format() -> None:
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"not music", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]

def test_analyze_accepts_a_recording_without_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    from musaic import pipeline
    from musaic.audio.transcriber import MidiNote

    def transcribe_audio(path: str | Path) -> list[MidiNote]:
        assert Path(path).read_bytes() == b"recording"
        return []

    monkeypatch.setattr(pipeline, "transcribe_audio", transcribe_audio)
    response = client.post(
        "/api/analyze",
        files={"file": ("recording.wav", b"recording", "audio/wav")},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["keyRoot"] is None
    assert result["progression"] == []
    assert result["suggestion"]["candidates"] == []


def test_chat_passes_analysis_into_rag(monkeypatch: pytest.MonkeyPatch) -> None:
    import json
    from collections.abc import Sequence

    from langchain_core.messages import BaseMessage

    from musaic.api.routers import chat

    def answer_question(
        query: str, history: Sequence[BaseMessage], *, context: str | None = None
    ) -> str:
        assert query == "Why E?"
        assert not history
        assert context is not None
        analysis = json.loads(context)
        assert analysis["progression"][0]["chord"] == "Am"
        assert analysis["suggestion"]["candidates"][0]["chord"] == "E"
        return "E is the major dominant in A minor."

    monkeypatch.setattr(chat, "answer_question", answer_question)
    response = client.post(
        "/api/chat",
        json={
            "query": "Why E?",
            "analysis": {
                "fileName": "recording.wav",
                "keyRoot": "A",
                "keyMode": "minor",
                "progression": [{"chord": "Am", "degree": "i", "start": 0, "end": 1}],
                "suggestion": {
                    "candidates": [{"chord": "E", "degree": "V"}],
                    "rationale": "Matched a reference progression.",
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {"response": "E is the major dominant in A minor."}
