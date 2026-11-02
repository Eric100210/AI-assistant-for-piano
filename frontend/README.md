# MusAIc — Frontend

Web interface for **MusAIc**, the assistant for piano improvisation and composition.

> **Status: connected to the FastAPI backend.** The full flow is functional (upload → analysis → chat). Network calls live in `src/api/client.ts` and go through `/api`, proxied by Vite to `http://localhost:8000`.

## Stack

- **React 18** + **TypeScript**
- **Vite** (dev server + build)
- **CSS Modules** for styling (no UI library, built from scratch)
- No runtime dependencies beyond React

## Getting started

The frontend needs the MusAIc API (see the root `README.md` and `backend/README.md`).
In two terminals from the repository root:

```bash
# 1) backend
make install
make api                   # http://localhost:8000

# 2) frontend
make install-frontend
make web                   # http://localhost:5173
```

Without the Makefile:

```bash
pip install -e "backend[api]" && musaic-api
cd frontend && npm install && npm run dev
```

Other commands:

```bash
npm run build      # production build in dist/
npm run preview    # preview the build
npm run typecheck  # type checking only
```

> `POST /api/chat` requires Ollama to be running (`llama3.2:3b`, `nomic-embed-text`)
> and the Chroma store to be built (`make ingest`). Without them, audio analysis
> still works, but the assistant replies with a fallback message.

## User flow

1. **Start**: only the hero and the upload area are shown.
2. **File upload**: an "Analyzing" panel appears, then the **Analysis** (key, chords, suggestion) and **MusAIc Assistant** (chat) panels are revealed.
3. **Chat**: ask a question (press Enter to send). Responses come from the local RAG via `POST /api/chat`.

## Structure

```text
frontend/
├── index.html
├── vite.config.ts            # build + proxy `/api` -> localhost:8000
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # global state + page composition
│   ├── types.ts              # domain types (mirror of backend/src/musaic/api/schemas.py)
│   ├── api/client.ts         # `fetch` calls to the FastAPI API
│   ├── styles/globals.css    # design tokens + reset
│   └── components/
│       ├── AppHeader.tsx        # header / brand
│       ├── Panel.tsx            # reusable section card
│       ├── UploadPanel.tsx      # step 1 — audio upload (drag & drop)
│       ├── AnalyzingPanel.tsx   # loading state
│       ├── AnalysisPanel.tsx    # step 2 — key, chords, suggestion
│       ├── ChatPanel.tsx        # step 3 — RAG conversation
│       └── Icons.tsx            # SVG icons
```

## API contract

The frontend consumes two endpoints served by `backend/src/musaic/api/`:

| Function (`src/api/client.ts`) | Endpoint | Body / response |
| --- | --- | --- |
| `analyzeAudio(file)` | `POST /api/analyze` | multipart `file` → `Analysis` |
| `sendMessage(query, history)` | `POST /api/chat` | `{ query, history }` → `{ response }` |

The types in `src/types.ts` describe these responses exactly (they are the mirror
of the Pydantic schemas in `backend/src/musaic/api/schemas.py`).

## Design

Dark "studio" theme: deep background, violet/cyan glows, typography with
`Space Grotesk` + `Inter`. Colors and radii are centralized in the design
tokens of `src/styles/globals.css` (`:root { --… }`).
