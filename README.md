# AI-assistant-for-piano

An AI assistant for piano improvisation and composition. It combines a RAG system built on my music theory resources with audio analysis that recognizes played chords and suggests suitable chord sequences for improvisation.

In practice, the audio analysis identifies the chords being played, a music engine suggests the next chord, and the RAG can provide further explanations or chord variations when the user wants to dive into the theory.

## Known challenges

- Converting chords to scale degrees after audio analysis: this requires knowing the key, which is not always possible when only chords are played.
- Separating the chord from the melody, especially when the chord is played at the same time as the first note of the melody.

## First version of the RAG

- Ingestion of my personal music theory courses (embeddings, vector database)
- Conversational RAG with chat history (ChatOllama), engine reference sheets, and separate theory retrieval

## First version of the audio analysis pipeline

- Download an `.mp3` file
- Transcribe it to MIDI data with the Basic Pitch model
- Detect the key and mode with the Krumhansl-Schmuckler key-finding algorithm
- Track background harmony using bass notes, sustained pitches and coordinated attacks
- Keep the current harmony through brief passing notes and mark sustained ambiguous passages
- Convert confirmed chords to scale degrees and suggest a continuation from the confirmed ending

Then: 

1. The engine compares the latest confirmed degrees with same-mode reference progressions. It prefers exact matches, then nearby examples that keep the current chord and differ by one earlier degree. For a two-chord ending, it can match a reference with that same ending. If an unclear passage interrupts the progression, earlier confirmed chords can help rank analogies without counting the passage as an exact match. The chat can explain the suggestion or offer variations.
2. We should be able to pass the simplified progression and the real one to the RAG, which directly suggests the next chord and variations based on the full real progression (not implemented yet, we inevitably go through the musical engine for now). This second option can also be used when the deterministic music engine does not find a relevant chord to suggest: the RAG must then propose one.

MIDI stands for Musical Instrument Digital Interface. It is structured data containing the note and the velocity at which it was played.

## Project structure

```
AI-assistant-for-piano/
├── backend/
│   ├── pyproject.toml          # dependencies and packaging
│   ├── src/musaic/             # installable package
│   │   ├── config.py           # single source of truth (paths, models, params)
│   │   ├── pipeline.py         # audio -> chord suggestion orchestration
│   │   ├── cli.py              # command-line entry point
│   │   ├── api/                # FastAPI app (HTTP layer, used by the frontend)
│   │   ├── audio/              # transcription + chord detection
│   │   ├── engine/             # key detection, degrees, chord suggestion
│   │   └── rag/                # ingestion, retrieval, chat
│   ├── tests/                  # pytest suites
│   ├── scripts/                # one-shot maintenance scripts
│   ├── data/
│   │   ├── rag_knowledge/      # markdown knowledge base (progressions, theory)
│   │   └── test_audio/         # sample audio
│   └── db/                     # persisted Chroma vector store (generated)
├── frontend/                   # React + Vite web interface
├── Makefile                    # common development commands
├── .gitignore
└── README.md
```

## Getting started

Ollama must be running locally with the `llama3.2:3b` (LLM) and `nomic-embed-text` (embeddings) models pulled.

```bash
pip install -e "backend[api]"            # or: make install

# Analyze an audio file and get chord suggestions (defaults to the test audio)
musaic                                   # or: python -m musaic
musaic path/to/audio.mp3
```

Knowledge-base maintenance:

```bash
make progressions                        # regenerate backend/src/musaic/engine/progressions.json
make ingest                              # update the Chroma index and prune removed chunks
```

After indexing with Ollama running, check the expected sources for the scale questions:

```bash
cd backend
MUSAIC_TEST_OLLAMA=1 python -m pytest tests/rag -q
```

Or directly:

```bash
cd backend
python scripts/build_progressions.py
python -m musaic.rag.ingestion
```

## API (FastAPI)

The HTTP layer that powers the web frontend lives in `backend/src/musaic/api/`.

```bash
pip install -e "backend[api]"            # installs fastapi, uvicorn, python-multipart
uvicorn musaic.api.main:app --reload --port 8000
# or, once installed:
musaic-api
# or:
make api
```

Then open <http://localhost:8000/docs> for the interactive API documentation.

| Endpoint | Purpose |
| --- | --- |
| `GET  /api/health`  | health check |
| `POST /api/analyze` | upload an audio file → `Analysis` (key, chords, suggestion) |
| `POST /api/chat`    | ask a theory question (RAG), stateless: the frontend sends the history and recording analysis |

### Run the app locally

In terminal 1 (start the FastAPI server with uvicorn):

```bash
make api           # or: musaic-api
```

In terminal 2:

```bash
make web           # or: cd frontend && npm install && npm run dev
# http://localhost:5173
```

The dev server proxies `/api` to `http://localhost:8000` (see
`frontend/vite.config.ts`), so start the API first. `POST /api/chat` also needs
Ollama running and the Chroma store built (`make ingest`).

## To do

Validate the tentative-key heuristic against labeled recordings and improve the engine's
chord-sequence suggestions.

It is also necessary to improve the RAG and the assistant, because for now it hallucinates a lot and does not always retrieve the most relevant documents. This will greatly improve the whole application.
