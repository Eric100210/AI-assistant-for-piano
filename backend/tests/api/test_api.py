"""Tests de l'API FastAPI.

Ils utilisent le ``TestClient`` : l'application tourne en mémoire, sans lancer
uvicorn. Ils sont ignorés automatiquement si FastAPI n'est pas installé.
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from musaic.api.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_validates_request_body():
    # Un corps sans "query" doit être rejeté par Pydantic (422) avant
    # même d'atteindre la logique RAG (donc sans besoin d'Ollama).
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_analyze_rejects_unknown_format():
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"pas de la musique", "text/plain")},
    )
    assert response.status_code == 400
