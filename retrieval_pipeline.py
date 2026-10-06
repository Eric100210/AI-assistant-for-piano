from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage

# Parameters
EMBEDDING_MODEL = "nomic-embed-text"
PERSIST_DIRECTORY = "db/chroma_db"
NB_RESULTS_RAG = 4

LLM_MODEL = "llama3.2:3b"
# 3 billion parameters here, try "llama3.2:7b" for a larger model


# Test parameters
TEST_QUERY = """
J’ai joué une progression I - VIm - IV : 
On me conseille de jouer maintenant un accord parmi les suivants : V - I. 
Explique l’effet créé par ces progressions possibles et propose des variantes pertinentes avec le style de musique qui leur est souvent associé.
"""
show_retrieved_docs = False

embedding_model = OllamaEmbeddings(
    model=EMBEDDING_MODEL, base_url="http://localhost:11434"
)

db = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"},
)

retriever = db.as_retriever(search_kwargs={"k": NB_RESULTS_RAG})
# retriever = db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.3, "k": NB_RESULTS_RAG})


def retrieve_documents(query):
    documents = retriever.invoke(query)
    return documents


def generate_response(query, documents):
    system_message = SystemMessage(
        content="Tu es un assistant musical qui fournit des explications et des suggestions basées sur les progressions musicales fournies."
    )
    human_message = HumanMessage(
        content=f"Demande: {query}\n\nFournis une réponse claire et aidante à partir des documents suivants :\n{[doc.page_content for doc in documents]}"
    )

    messages = [system_message, human_message]
    llm = OllamaLLM(model=LLM_MODEL, base_url="http://localhost:11434")
    response = llm.invoke(messages)
    return response


if __name__ == "__main__":
    relevant_docs = retrieve_documents(TEST_QUERY)
    if show_retrieved_docs:
        for i, doc in enumerate(relevant_docs):
            print(f"Document {i + 1}:")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")
            print("-" * 80)

    response = generate_response(TEST_QUERY, relevant_docs)
    print(f"Response: {response}")
