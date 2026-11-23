// =============================================================================
// Types du domaine MusAIc
// -----------------------------------------------------------------------------
// Ces types décrivent les données renvoyées par le back-end FastAPI. Ils sont
// le miroir de `backend/src/musaic/api/schemas.py` : si tu changes l'un, change l'autre.
// =============================================================================

/** Un accord détecté, exprimé à la fois en degré et en nom d'accord. */
export interface ChordEvent {
  /** Degré dans la tonalité, ex. "I", "VIm", "IV", "vii°". */
  degree: string;
  /** Nom de l'accord, ex. "C", "Am", "F". */
  chord: string;
  referenceMatches: number;
  example: string[];
  matchKind: "exact" | "similar" | "short" | "gap";
  referenceId: string | null;
}

export interface DetectedChord {
  chord: string | null;
  degree: string | null;
  start: number;
  end: number;
}

/** Résultat complet d'une analyse audio. */
export interface Analysis {
  /** Nom du fichier analysé. */
  fileName: string;
  /** Tonique détectée, ex. "C", "F#". */
  keyRoot: string | null;
  /** Mode détecté. */
  keyMode: "major" | "minor" | null;
  keyStatus: "estimated" | "tentative" | "undetermined";
  alternativeKey: string | null;
  /** Progression d'accords détectée, dans l'ordre chronologique. */
  progression: DetectedChord[];
  /** Suggestion du moteur musical pour la suite. */
  suggestion: {
    /** Accords proposés pour la suite de la progression, dans l'ordre. */
    candidates: ChordEvent[];
    /** Explication courte de la provenance de la suggestion. */
    rationale: string;
  };
}

/** Rôles possibles d'un message de chat. */
export type ChatRole = "user" | "assistant";

/** Un message dans la conversation avec l'assistant théorique (RAG). */
export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
}
