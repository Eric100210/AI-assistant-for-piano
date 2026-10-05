import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import re
import json
import yaml

CHUNK_SECTIONS = {
    "structure": [
        "Structure harmonique",
        "Exemples",
        "Variantes",
    ],
    "interpretation": [
        "Caractère musical",
        "Utilisation",
    ],
}

EMBEDDING_MODEL = "nomic-embed-text"
PERSIST_DIRECTORY = "db/chroma_db"


# For chunking version with fixed size
RAG_DIRECTORY = "RAG_knowledge"
CHUNK_SIZE = 1000



def load_documents_from_directory(directory_path):
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"The directory '{directory_path}' does not exist.")
    loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    if len(documents) == 0:
        raise ValueError(f"No .md documents found in the directory '{directory_path}'.")
    return documents



def split_document_in_two_chunks(document):
    content = document.page_content

    # 1. Separate the YAML front matter from the Markdown content
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        raise ValueError("Front matter YAML introuvable.")

    metadata = yaml.safe_load(match.group(1)) or {}
    markdown = content[match.end():]

    # 2. Get the main title (first line starting with #)
    title_match = re.search(r"^# .+$", markdown, re.MULTILINE)
    if not title_match:
        raise ValueError("Titre principal introuvable.")

    title = title_match.group(0)

    # 3. Split the Markdown content into sections based on headings (##)
    headings = list(re.finditer(r"^## (.+)$", markdown, re.MULTILINE))
    sections = {}

    for i, heading in enumerate(headings):
        start = heading.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(markdown)

        section_name = heading.group(1).strip()
        section_content = markdown[start:end].strip()
        sections[section_name] = section_content

    # 4. Build chunks based on the defined CHUNK_SECTIONS
    progression_id = metadata["id"]
    progression_degrees = metadata.get("degres", [])
    degrees_text = " – ".join(progression_degrees)

    chunks = []

    for chunk_type, section_names in CHUNK_SECTIONS.items():
        selected_sections = [
            sections[name]
            for name in section_names
            if name in sections
        ]

        if not selected_sections:
            continue

        chunk_id = f"{progression_id}::{chunk_type}"
        related_type = (
            "interpretation" if chunk_type == "structure" else "structure"
        )

        page_content = (
            f"{title}\n\n"
            f"Progression : {degrees_text}\n"
            f"Identifiant : {progression_id}\n"
            f"Type de contenu : {chunk_type}\n\n"
            + "\n\n".join(selected_sections)
        )

        chunk_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                chunk_metadata[key] = json.dumps(
                    value, ensure_ascii=False
                )
            elif value is not None:
                chunk_metadata[key] = value

        chunk_metadata.update({
            "chunk_id": chunk_id,
            "chunk_type": chunk_type,
            "related_to": f"{progression_id}::{related_type}",
        })

        chunk_metadata.update(document.metadata)

        chunks.append(Document(
            page_content=page_content,
            metadata=chunk_metadata,
        ))

    return chunks
        

def create_chunks_of_fixed_size(documents, chunk_size=CHUNK_SIZE, chunk_overlap=0):
    """Not used : replaced by a fixed split in two chunks"""
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    if chunks is None or len(chunks) == 0:
        raise ValueError("No chunks were created from the documents.")
    return chunks


def create_chunks(documents):
    all_chunks = []
    for document in documents:
        chunks = split_document_in_two_chunks(document)
        all_chunks.extend(chunks)
    return all_chunks


def create_embeddings(chunks, model):
    embeddings = OllamaEmbeddings(model=model, base_url="http://localhost:11434")
    vector_store = Chroma.from_documents(chunks, embeddings, persist_directory=PERSIST_DIRECTORY, collection_metadata={"hnsw:space": "cosine"})
    return vector_store

def main():
    documents = load_documents_from_directory(RAG_DIRECTORY)
    chunks = create_chunks(documents)
    for chunk in chunks:
        print(f"Chunk ID: {chunk.metadata.get('chunk_id')}")
        print(f"Chunk Type: {chunk.metadata.get('chunk_type')}")
        print(f"Related To: {chunk.metadata.get('related_to')}")
        print(f"Content:\n{chunk.page_content[:200]}...\n")
        print("-" * 80)

    vector_store = create_embeddings(chunks, model = EMBEDDING_MODEL)

if __name__ == "__main__":
    main()