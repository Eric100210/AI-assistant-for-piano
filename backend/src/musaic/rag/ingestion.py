"""Knowledge-base ingestion: load markdown, chunk it and persist embeddings."""

import json
import os
import re
from collections.abc import Iterable

import yaml
from filelock import FileLock
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

from musaic.config import PERSIST_DIRECTORY, RAG_KNOWLEDGE_DIR
from musaic.rag.embeddings import get_embedding_model

CHUNK_SECTIONS = {
    "structure": [
        "Structure harmonique",
        "Exemples",
    ],
    "interpretation": [
        "Variantes",
        "Caractère musical",
        "Utilisation",
    ],
}


def load_documents_from_directory(directory_path: str) -> list[Document]:
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"The directory '{directory_path}' does not exist.")
    loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    if len(documents) == 0:
        raise ValueError(f"No .md documents found in the directory '{directory_path}'.")
    return documents


def split_document(document: Document) -> list[Document]:
    content = document.page_content

    # 1. Separate the YAML front matter from the Markdown content
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        raise ValueError("Front matter YAML introuvable.")

    metadata = yaml.safe_load(match.group(1)) or {}
    markdown = content[match.end() :]

    if metadata.get("type") != "progression":
        return [
            Document(
                page_content=markdown.strip(),
                metadata={
                    **document.metadata,
                    "chunk_id": metadata["id"],
                    "chunk_type": "theory",
                },
            )
        ]

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
            sections[name] for name in section_names if name in sections
        ]

        if not selected_sections:
            continue

        chunk_id = f"{progression_id}::{chunk_type}"

        page_content = (
            f"{title}\n\n"
            f"Progression : {degrees_text}\n"
            f"Identifiant : {progression_id}\n"
            f"Type de contenu : {chunk_type}\n\n" + "\n\n".join(selected_sections)
        )

        chunk_metadata: dict[str, object] = {}
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                chunk_metadata[key] = json.dumps(value, ensure_ascii=False)
            elif value is not None:
                chunk_metadata[key] = value

        chunk_metadata.update(
            {
                "chunk_id": chunk_id,
                "chunk_type": chunk_type,
            }
        )

        chunk_metadata.update(document.metadata)

        chunks.append(
            Document(
                page_content=page_content,
                metadata=chunk_metadata,
            )
        )

    return chunks


def create_chunks(documents: Iterable[Document]) -> list[Document]:
    all_chunks = []
    for document in documents:
        chunks = split_document(document)
        all_chunks.extend(chunks)
    return all_chunks


def create_embeddings(chunks: list[Document]) -> Chroma:
    ids = [str(chunk.metadata["chunk_id"]) for chunk in chunks]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Ingestion requires non-empty, unique chunk IDs.")

    # Serialize writers so a concurrent run cannot prune another run's chunks.
    PERSIST_DIRECTORY.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(PERSIST_DIRECTORY.with_suffix(".lock"))):
        vector_store = Chroma(
            persist_directory=str(PERSIST_DIRECTORY),
            embedding_function=get_embedding_model(),
            collection_metadata={"hnsw:space": "cosine"},
        )
        previous_ids = set(vector_store.get(include=[])["ids"])
        vector_store.add_documents(chunks, ids=ids)
        stale_ids = sorted(previous_ids.difference(ids))
        if stale_ids:
            vector_store.delete(ids=stale_ids)

    return vector_store


def main() -> Chroma:
    documents = load_documents_from_directory(str(RAG_KNOWLEDGE_DIR))
    chunks = create_chunks(documents)
    vector_store = create_embeddings(chunks)
    print(f"Indexed {len(chunks)} chunks from {len(documents)} documents.")
    return vector_store


if __name__ == "__main__":
    main()
