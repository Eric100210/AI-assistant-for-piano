"""Vector-store retrieval and RAG response generation.

The vector store and retriever are created lazily (on first use) so that
importing this module does not open the Chroma database.
"""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage

from musaic.config import NB_RESULTS_RAG, PERSIST_DIRECTORY
from musaic.rag.embeddings import get_embedding_model
from musaic.rag.llm import get_llm


@lru_cache(maxsize=1)
def get_vector_store():
    """Open the persisted Chroma store on first use."""
    return Chroma(
        persist_directory=str(PERSIST_DIRECTORY),
        embedding_function=get_embedding_model(),
        collection_metadata={"hnsw:space": "cosine"},
    )


@lru_cache(maxsize=1)
def get_retriever():
    """Return the retriever built from the vector store."""
    return get_vector_store().as_retriever(search_kwargs={"k": NB_RESULTS_RAG})
    # alternative: search_type="similarity_score_threshold",
    #              search_kwargs={"score_threshold": 0.3, "k": NB_RESULTS_RAG}


def retrieve_documents(query):
    return get_retriever().invoke(query)


def generate_response(query, documents):
    system_message = SystemMessage(
        content="Tu es un assistant musical qui fournit des explications et des suggestions basées sur les progressions musicales fournies."
    )
    human_message = HumanMessage(
        content=f"Demande: {query}\n\nFournis une réponse claire et aidante à partir des documents suivants (s'ils sont pertinents par rapport à la demande):\n{[doc.page_content for doc in documents]}"
    )

    messages = [system_message, human_message]
    return get_llm().invoke(messages)


if __name__ == "__main__":
    test_query = (
        "J'ai joué une progression I - VIm - IV. On me conseille de jouer "
        "maintenant un accord parmi V - I. Explique l'effet créé par ces "
        "progressions possibles et propose des variantes pertinentes."
    )
    relevant_docs = retrieve_documents(test_query)
    response = generate_response(test_query, relevant_docs)
    print(f"Response: {response}")
