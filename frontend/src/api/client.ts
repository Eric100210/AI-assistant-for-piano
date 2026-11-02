import type { Analysis, ChatMessage } from "../types";

// =============================================================================
// Client API
// -----------------------------------------------------------------------------
// Appels réels au back-end FastAPI (`backend/src/musaic/api`).
//
// En développement, le serveur Vite proxyfie `/api` vers http://localhost:8000
// (voir `vite.config.ts`). Il faut donc lancer l'API en parallèle du front :
//
//     musaic-api        # ou : uvicorn musaic.api.main:app --reload --port 8000
//     npm run dev       # dans frontend/
//
// ⚠️ `POST /api/chat` a besoin qu'Ollama tourne et que la base Chroma soit
// construite (`make ingest`) ; sinon l'assistant répondra
// par le message d'erreur de repli.
// =============================================================================

/** Préfixe de l'API (le dev server Vite proxyfie `/api` vers FastAPI). */
export const API_BASE = "/api";

/** Récupère un message d'erreur lisible depuis une réponse non-OK (FastAPI). */
async function errorMessage(res: Response): Promise<string> {
  try {
    const payload = (await res.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") return payload.detail;
  } catch {
    // réponse non-JSON : on retombe sur le code HTTP
  }
  return `Error ${res.status}`;
}

/** Analyse un fichier audio et renvoie le résultat (tonalité, accords, suite). */
export async function analyzeAudio(file: File): Promise<Analysis> {
  const form = new FormData();
  form.append("file", file);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: form });
  } catch {
    throw new Error(
      "Analysis server unreachable. Start the MusAIc API on port 8000.",
    );
  }

  if (!res.ok) throw new Error(await errorMessage(res));
  return (await res.json()) as Analysis;
}

/** Envoie une question à l'assistant et renvoie sa réponse. */
export async function sendMessage(
  query: string,
  history: ChatMessage[],
): Promise<string> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, history }),
    });
  } catch {
    throw new Error(
      "Assistant unreachable. Check that the API and Ollama are running.",
    );
  }

  if (!res.ok) throw new Error(await errorMessage(res));
  return ((await res.json()) as { response: string }).response;
}
