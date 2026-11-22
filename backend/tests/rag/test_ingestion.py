import os
from pathlib import Path

import pytest
from langchain_core.documents import Document

from musaic.config import RAG_KNOWLEDGE_DIR
from musaic.rag.ingestion import create_chunks


def test_scale_lessons_are_indexed() -> None:
    paths = sorted((RAG_KNOWLEDGE_DIR / "theory").glob("*.md"))
    chunks = create_chunks(
        Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
        for path in paths
    )

    assert {chunk.metadata["chunk_id"] for chunk in chunks} == {
        "gamme_majeure",
        "gamme_mineure",
    }
    assert all(chunk.page_content.startswith("#") for chunk in chunks)


def test_reingestion_replaces_stale_chunks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from langchain_core.embeddings import FakeEmbeddings

    from musaic.rag import ingestion

    monkeypatch.setattr(ingestion, "PERSIST_DIRECTORY", tmp_path / "chroma")
    monkeypatch.setattr(ingestion, "get_embedding_model", lambda: FakeEmbeddings(size=8))
    lesson = Document(page_content="First version", metadata={"chunk_id": "lesson"})
    stale = Document(page_content="Removed", metadata={"chunk_id": "obsolete"})
    store = ingestion.create_embeddings([lesson, stale])
    store.add_documents([lesson], ids=["legacy-random-id"])

    updated = Document(page_content="Updated version", metadata={"chunk_id": "lesson"})
    for _ in range(2):
        snapshot = ingestion.create_embeddings([updated]).get(include=["documents"])
        assert snapshot["ids"] == ["lesson"]
        assert snapshot["documents"] == ["Updated version"]


@pytest.mark.skipif(
    os.environ.get("MUSAIC_TEST_OLLAMA") != "1",
    reason="Requires local Ollama and the Chroma index built by make ingest.",
)
@pytest.mark.parametrize(
    ("query", "expected_source"),
    [
        ("Quels intervalles définissent la gamme majeure naturelle ?", "gamme_majeure"),
        ("Quels intervalles composent la gamme mineure naturelle ?", "gamme_mineure"),
    ],
)
def test_retrieval_finds_expected_scale_lesson(query: str, expected_source: str) -> None:
    from musaic.config import PERSIST_DIRECTORY
    from musaic.rag.retrieval import retrieve_documents

    assert PERSIST_DIRECTORY.is_dir(), "Run make ingest before testing retrieval."
    matches = retrieve_documents(query)
    assert expected_source in {document.metadata["chunk_id"] for document in matches}
