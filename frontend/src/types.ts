// =============================================================================
// Types du domaine MusAIc
// -----------------------------------------------------------------------------
// Ces types décrivent les données renvoyées par le back-end FastAPI. Ils sont
// le miroir de `src/musaic/api/schemas.py` : si tu changes l'un, change l'autre.
// =============================================================================

/** Un accord détecté, exprimé à la fois en degré et en nom d'accord. */
export interface ChordEvent {
  /** Degré dans la tonalité, ex. "I", "VIm", "IV", "vii°". */
  degree: string;
  /** Nom de l'accord, ex. "C", "Am", "F". */
  chord: string;
}

/** Résultat complet d'une analyse audio. */
export interface Analysis {
  /** Nom du fichier analysé. */
  fileName: string;
  /** Durée formatée, ex. "0:42". */
  durationLabel: string;
  /** Tonique détectée, ex. "C", "F#". */
  keyRoot: string;
  /** Mode détecté. */
  keyMode: "majeur" | "mineur";
  /** Indice de confiance de la détection (0 → 1). */
  confidence: number;
  /** Progression d'accords détectée, dans l'ordre chronologique. */
  progression: ChordEvent[];
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
