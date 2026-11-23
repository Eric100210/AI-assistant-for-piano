"""Vector-store retrieval and RAG response generation.

The vector store and retriever are created lazily (on first use) so that
importing this module does not open the Chroma database.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.vectorstores import VectorStoreRetriever

from musaic.config import NB_RESULTS_RAG, PERSIST_DIRECTORY, SEMIS
from musaic.engine.musical_engine import degrees_to_chords
from musaic.rag.embeddings import get_embedding_model
from musaic.rag.llm import get_llm


@dataclass(frozen=True)
class RecordingContext:
    summary: str
    key_mode: Literal["major", "minor"] | None
    reference_ids: tuple[str, ...] = ()
    key_root: str | None = None
    dominant_reference_id: str | None = None


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    """Open the persisted Chroma store on first use."""
    return Chroma(
        persist_directory=str(PERSIST_DIRECTORY),
        embedding_function=get_embedding_model(),
        collection_metadata={"hnsw:space": "cosine"},
    )


@lru_cache(maxsize=1)
def get_retriever() -> VectorStoreRetriever:
    """Return the retriever built from the vector store."""
    return get_vector_store().as_retriever(search_kwargs={"k": NB_RESULTS_RAG})
    # alternative: search_type="similarity_score_threshold",
    #              search_kwargs={"score_threshold": 0.3, "k": NB_RESULTS_RAG}


def retrieve_documents(query: str) -> list[Document]:
    return get_retriever().invoke(query)


def invoke_text(messages: Sequence[BaseMessage]) -> str:
    text = get_llm().invoke(list(messages)).text
    return text if isinstance(text, str) else text()


def make_standalone_query(query: str, history: Sequence[BaseMessage]) -> str:
    messages = (
        SystemMessage(
            content="Given the chat history, rewrite the new question so that it is standalone and understandable without context:"
        ),
        *history,
        HumanMessage(content=f"New question: {query}"),
    )
    return invoke_text(messages).strip()


def retrieve_answer_sources(
    query: str, context: RecordingContext | None
) -> list[Document]:
    sources: dict[str, Document] = {}

    if context:
        store = get_vector_store()
        ids = [
            f"{reference_id}::{section}"
            for reference_id in dict.fromkeys(context.reference_ids)
            for section in ("structure", "interpretation")
        ]
        if ids:
            for document in store.get_by_ids(ids):
                sources[document.metadata["chunk_id"]] = document
        if context.key_mode:
            tonalite = "mineure" if context.key_mode == "minor" else "majeure"
            lessons = store.similarity_search(
                query,
                k=3,
                filter={"$and": [{"chunk_type": "theory"}, {"tonalite": tonalite}]},
            )
            for document in lessons:
                sources[document.metadata["chunk_id"]] = document

    for document in retrieve_documents(query):
        source_id = document.metadata.get("chunk_id") or document.page_content
        sources.setdefault(source_id, document)
    return list(sources.values())


def generate_response(
    query: str,
    documents: Sequence[Document],
    *,
    context: RecordingContext | None = None,
    standalone_query: str | None = None,
) -> str:
    instructions = (
        "You are a practical piano improvisation teacher. Reply in the language of the original "
        "question unless the user requests another. Treat analysis and sources as evidence, "
        "and use only the ones relevant to the question. When discussing a suggested chord, "
        "distinguish what the analysis detected, what the engine proposed, and what the theory "
        "explains. Present approximate matches as analogies. Give a short playable example and "
        "a contrasting variation when that helps. Check chord spellings and use Roman-numeral "
        "case to distinguish major and minor chords. Examples from a different key must be "
        "transposed before use. Always follow the verified facts when provided. "
        "Cite the source IDs you actually use in "
        "square brackets. If the evidence is insufficient, explain what remains uncertain."
    )
    if context and context.key_mode == "minor" and context.key_root in SEMIS:
        key = f"{context.key_root}m"
        natural, harmonic = degrees_to_chords(key, ["v", "V"])
        instructions += (
            f" Verified facts for this key: in {key} natural minor, v is {natural}. "
            f"In {key} harmonic minor, V is {harmonic}, with the raised seventh of the scale. "
            f"When comparing these sounds, use {key} → {natural} → {key} and "
            f"{key} → {harmonic} → {key} as the playable examples."
        )
    question = f"Original question: {query}"
    if standalone_query and standalone_query != query:
        question += f"\nContextual interpretation (use only if consistent): {standalone_query}"
    if context:
        question += f"\nRecording analysis: {context.summary}"
    excerpts = "\n\n".join(
        f"[{doc.metadata.get('chunk_id', 'source')}]\n{doc.page_content}" for doc in documents
    )
    human_message = HumanMessage(content=f"{question}\n\nSources:\n{excerpts}")
    return invoke_text([SystemMessage(content=instructions), human_message])


def explain_minor_dominant(
    query: str, context: RecordingContext, documents: Sequence[Document]
) -> str | None:
    """Answer the supported minor-dominant comparison directly from verified facts."""
    if context.key_mode != "minor" or context.key_root not in SEMIS:
        return None
    if not context.dominant_reference_id:
        return None

    question = query.casefold()
    french = "mineur naturel" in question and "accord" in question
    english = "natural minor" in question and "chord" in question
    if not (french or english):
        return None
    if not any(word in question for word in ("propos", "suggest", "recommend", " v ")):
        return None
    if any(word in question for word in ("anglais", "english", "français", "french")):
        return None

    sources = {document.metadata.get("chunk_id") for document in documents}
    reference = f"{context.dominant_reference_id}::structure"
    natural_source = "gamme_mineure::gamme-mineure-naturelle"
    harmonic_source = "gamme_mineure::gamme-mineure-harmonique"
    if not {reference, natural_source, harmonic_source} <= sources:
        return None

    key = f"{context.key_root}m"
    natural, harmonic = degrees_to_chords(key, ["v", "V"])
    if french:
        return (
            f"Le moteur reprend la dominante **V** de sa progression de référence [{reference}]. "
            f"En mineur harmonique, **{harmonic}** est majeur : la septième de la gamme est relevée "
            f"et attire l’oreille vers la tonique [{harmonic_source}]. Essaie **{key} → {harmonic} → {key}**.\n\n"
            f"Pour rester en mineur naturel, joue **{natural} (v)**. Compare avec "
            f"**{key} → {natural} → {key}** : le retour est moins tendu [{natural_source}]."
        )
    return (
        f"The engine follows the **V** in its reference progression [{reference}]. "
        f"In harmonic minor, **{harmonic}** is major: the raised seventh leads back to the tonic "
        f"[{harmonic_source}]. Try **{key} → {harmonic} → {key}**.\n\n"
        f"To stay in natural minor, play **{natural} (v)**. Compare with "
        f"**{key} → {natural} → {key}**, which has a gentler return [{natural_source}]."
    )


def answer_question(
    query: str, history: Sequence[BaseMessage], *, context: RecordingContext | None = None
) -> str:
    standalone = make_standalone_query(query, history) if history else query
    documents = retrieve_answer_sources(standalone or query, context)
    if context and (answer := explain_minor_dominant(query, context, documents)):
        return answer
    return generate_response(query, documents, context=context, standalone_query=standalone)
