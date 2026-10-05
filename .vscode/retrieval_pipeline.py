from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


EMBEDDING_MODEL = "nomic-embed-text"
PERSIST_DIRECTORY = "db/chroma_db"
NB_RESULTS_RAG = 4

TEST_QUERY = """
J’ai joué une progression I - VIm - IV : 
On me conseille de jouer maintenant un accord parmi les suivants : V - I. 
Explique l’effet créé par ces progressions possibles et propose des variantes pertinentes avec le style de musique qui leur est souvent associé.
"""

embedding_model = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url="http://localhost:11434")

db = Chroma(persist_directory=PERSIST_DIRECTORY, 
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"})

retriever = db.as_retriever(search_kwargs={"k": NB_RESULTS_RAG})
# retriever = db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.3, "k": NB_RESULTS_RAG})

def retrieve_documents(query):
    documents = retriever.invoke(query)
    return documents

if __name__ == "__main__":
    relevant_docs = retrieve_documents(TEST_QUERY)
    for i, doc in enumerate(relevant_docs):
        print(f"Document {i+1}:")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")
        print("-" * 80)