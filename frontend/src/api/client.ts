import type { Analysis, ChatMessage } from "../types";
import { sampleAnalysis, sampleExplanation } from "../data/sample";

// =============================================================================
// Client API
// -----------------------------------------------------------------------------
// ⚠️ ÉTAT ACTUEL : MOCK.
// Ces deux fonctions simulent le back-end pour que le front soit entièrement
// navigable (upload → analyse → chat). Le jour où ton API FastAPI tourne,
// remplace UNIQUEMENT le corps de chaque fonction par le vrai appel `fetch`
// (fourni en commentaire). Les signatures ne changent pas : aucun composant
// n'a besoin d'être modifié.
// =============================================================================

/** Préfixe de l'API (le dev server Vite proxyfie `/api` vers FastAPI). */
export const API_BASE = "/api";
const MOCK_DELAY_MS = 900;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Analyse un fichier audio et renvoie le résultat (tonalité, accords, suite). */
export async function analyzeAudio(file: File): Promise<Analysis> {
  // ---------------------------------------------------------------------------
  // TODO (toi) — remplace le mock ci-dessous par l'appel réel :
  //
  //   const form = new FormData();
  //   form.append("file", file);
  //   const res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: form });
  //   if (!res.ok) throw new Error(`Analyse échouée (${res.status})`);
  //   return (await res.json()) as Analysis;
  // ---------------------------------------------------------------------------
  await delay(MOCK_DELAY_MS);
  return { ...sampleAnalysis, fileName: file.name };
}

/** Envoie une question à l'assistant et renvoie sa réponse. */
export async function sendMessage(
  query: string,
  history: ChatMessage[],
): Promise<string> {
  // ---------------------------------------------------------------------------
  // TODO (toi) — remplace le mock ci-dessous par l'appel réel :
  //
  //   const res = await fetch(`${API_BASE}/chat`, {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify({ query, history }),
  //   });
  //   if (!res.ok) throw new Error(`Chat échoué (${res.status})`);
  //   return ((await res.json()) as { response: string }).response;
  // ---------------------------------------------------------------------------
  void query;
  void history;
  await delay(MOCK_DELAY_MS);
  return sampleExplanation;
}
