"""Single source of truth for project configuration.

Models, RAG parameters and paths are defined once here and imported
everywhere else. All paths are absolute, so they work regardless of the
current working directory.

``PROJECT_ROOT`` is the repository root (where ``RAG_knowledge/``,
``test_data/`` and ``db/`` live). It can be overridden with the ``MUSAIC_ROOT``
environment variable when the package is not used from a checkout.
"""

import os
from pathlib import Path

# Package directory (.../src/musaic) and repository root (.../)
PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.getenv("MUSAIC_ROOT", PACKAGE_ROOT.parents[1])).resolve()

# --- Knowledge base directories ---
RAG_KNOWLEDGE_DIR = PROJECT_ROOT / "RAG_knowledge"
PROGRESSIONS_DIR = RAG_KNOWLEDGE_DIR / "progressions"
THEORY_DIR = RAG_KNOWLEDGE_DIR / "theory"

# Generated musical-engine data (shipped as package data)
PROGRESSIONS_JSON = PACKAGE_ROOT / "engine" / "progressions.json"

# Persisted vector store (generated artifact, not versioned)
DB_DIR = PROJECT_ROOT / "db"
PERSIST_DIRECTORY = DB_DIR / "chroma_db"

# Test data
TEST_DATA_DIR = PROJECT_ROOT / "test_data"
TEST_AUDIO_PATH = TEST_DATA_DIR / "test_audio.mp3"
TEST_AUDIO_LONGER_PATH = TEST_DATA_DIR / "test_audio_longer.mp3"

# --- Models ---
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3.2:3b"  # try "llama3.2:7b" for a larger model
EMBEDDING_MODEL = "nomic-embed-text"

# --- RAG parameters ---
NB_RESULTS_RAG = 4
CHUNK_SIZE = 1000

# --- Music constants ---
SEMIS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
