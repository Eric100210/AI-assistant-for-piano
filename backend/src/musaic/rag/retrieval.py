"""Vector-store retrieval and RAG response generation.

The vector store and retriever are created lazily (on first use) so that
importing this module does not open the Chroma database.
"""

from collections.abc import Sequence
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.vectorstores import VectorStoreRetriever

from musaic.config import NB_RESULTS_RAG, PERSIST_DIRECTORY
from musaic.rag.embeddings import get_embedding_model
from musaic.rag.llm import get_llm


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


def make_standalone_query(query: str, history: Sequence[BaseMessage]) -> str:
    messages = (
        SystemMessage(
            content="Given the chat history, rewrite the new question so that it is standalone and understandable without context:"
        ),
        *history,
        HumanMessage(content=f"New question: {query}"),
    )
    result = get_llm().invoke(messages)
    return result.strip()


def generate_response(query: str, documents: Sequence[Document]) -> str:
    system_message = SystemMessage(
        content="You are a music assistant that provides explanations and suggestions based on the provided chord progressions. Answer in English unless the user explicitly asks for another language."
    )
    human_message = HumanMessage(
        content=f"Request: {query}\n\nProvide a clear and helpful answer using the following documents (if they are relevant to the request):\n{[doc.page_content for doc in documents]}"
    )

    messages = [system_message, human_message]
    return get_llm().invoke(messages)


if __name__ == "__main__":
    test_query = (
        "I played a I - VIm - IV progression. I'm advised to play one of "
        "V - I next. Explain the effect of these possible progressions and "
        "suggest relevant variations."
    )
    relevant_docs = retrieve_documents(test_query)
    response = generate_response(test_query, relevant_docs)
    print(f"Response: {response}")
