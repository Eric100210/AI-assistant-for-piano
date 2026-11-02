# MusAIc — Backend

The Python core of **MusAIc**: audio analysis, music engine and RAG, exposed to
the web interface through a FastAPI API.

## Stack

- **Python ≥ 3.10**, `setuptools` packaging (`src/` layout)
- **FastAPI** + **uvicorn** for the HTTP layer
- **basic-pitch** / **pychord** for audio analysis and chord detection
- **LangChain** + **Chroma** + **Ollama** for the RAG

## Getting started

From the repository root:

```bash
make install            # pip install -e "backend[api]"
make api                # musaic-api -> http://localhost:8000
```

Without the Makefile:

```bash
pip install -e "backend[api]"
musaic-api
```

Interactive API documentation: <http://localhost:8000/docs>.

## Useful commands

```bash
make test               # tests (pytest)
make ingest             # rebuild the Chroma store
make progressions       # regenerate backend/src/musaic/engine/progressions.json
```

Direct equivalents:

```bash
cd backend
pytest
python -m musaic.rag.ingestion
python scripts/build_progressions.py
```

## Structure

```text
backend/
├── pyproject.toml          # packaging + dependencies + pytest config
├── src/musaic/             # importable Python package
│   ├── config.py           # single source of truth for paths, models and parameters
│   ├── pipeline.py         # audio -> chord suggestion
│   ├── cli.py              # `musaic` entry point
│   ├── api/                # FastAPI app (routers, schemas, services)
│   ├── audio/              # transcription + chord detection
│   ├── engine/             # key, degrees, suggestions
│   └── rag/                # ingestion, retrieval, chat
├── tests/                  # pytest test suites
├── scripts/                # maintenance scripts
├── data/                   # knowledge base + test audio
└── db/                     # persisted Chroma store (generated, not versioned)
```

`config.py` resolves paths from `backend/`, so `data/` and `db/` are always found
regardless of the current working directory. The `MUSAIC_ROOT` environment
variable can override this root.

## Required Ollama models

```bash
ollama pull llama3.2:3b       # LLM
ollama pull nomic-embed-text  # embeddings
```

`POST /api/chat` requires Ollama to be running and the Chroma store to be built
(`make ingest`). Without them, audio analysis still works, but the assistant
replies with a fallback message.
