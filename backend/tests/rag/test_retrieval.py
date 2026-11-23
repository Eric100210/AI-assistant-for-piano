import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage

from musaic.rag import retrieval
from musaic.rag.retrieval import RecordingContext


def test_followup_joins_engine_reference_and_theory(monkeypatch: pytest.MonkeyPatch) -> None:
    question = "Pourquoi cet accord ?"
    standalone = "Pourquoi Ré majeur en sol mineur ?"
    reference = Document(
        page_content="i – iv – i – V", metadata={"chunk_id": "prog_min__024::structure"}
    )
    theory = Document(
        page_content="Le fa dièse est la sensible.",
        metadata={"chunk_id": "gamme_mineure::gamme-mineure-harmonique"},
    )
    context = RecordingContext("Sol mineur. D (V), proposé par analogie.", "minor", ("prog_min__024",), "G")

    class Store:
        def get_by_ids(self, ids: list[str]) -> list[Document]:
            assert ids == ["prog_min__024::structure", "prog_min__024::interpretation"]
            return [reference]

        def similarity_search(
            self, query: str, *, k: int, filter: dict[str, list[dict[str, str]]]
        ) -> list[Document]:
            assert query == standalone
            assert k == 3
            assert filter == {"$and": [{"chunk_type": "theory"}, {"tonalite": "mineure"}]}
            return [theory]

    monkeypatch.setattr(retrieval, "get_vector_store", Store)
    monkeypatch.setattr(retrieval, "make_standalone_query", lambda *_: standalone)

    def retrieve_documents(query: str) -> list[Document]:
        assert query == standalone
        return [reference]

    monkeypatch.setattr(retrieval, "retrieve_documents", retrieve_documents)

    class Model:
        def invoke(self, messages: list[BaseMessage]) -> AIMessage:
            system, human = messages
            assert "language of the original question" in system.content
            assert "in Gm natural minor, v is Dm" in system.content
            assert "In Gm harmonic minor, V is D" in system.content
            assert question in human.content
            assert context.summary in human.content
            assert human.content.count("[prog_min__024::structure]") == 1
            assert "[gamme_mineure::gamme-mineure-harmonique]" in human.content
            return AIMessage("Le fa♯ de Ré majeur peut monter vers sol.")

    monkeypatch.setattr(retrieval, "get_llm", Model)
    assert retrieval.answer_question(question, [AIMessage("Essaie D.")], context=context).startswith(
        "Le fa♯"
    )


def test_minor_dominant_comparison_uses_verified_examples(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = (
        "prog_min__024::structure",
        "gamme_mineure::gamme-mineure-naturelle",
        "gamme_mineure::gamme-mineure-harmonique",
    )
    documents = [Document(page_content=source, metadata={"chunk_id": source}) for source in ids]
    monkeypatch.setattr(retrieval, "retrieve_answer_sources", lambda *_: documents)
    context = RecordingContext(
        "Gm. D (V), proposé par analogie.", "minor", ("prog_min__024",), "G", "prog_min__024"
    )

    response = retrieval.answer_question(
        "Pourquoi Ré majeur est-il proposé ? Quel accord essayer pour rester en mineur naturel ?",
        [],
        context=context,
    )

    assert "**Gm → D → Gm**" in response
    assert "**Dm (v)**" in response
    assert "**Gm → Dm → Gm**" in response
    assert all(f"[{source}]" in response for source in ids)
