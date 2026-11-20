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
