import type { Analysis, ChatMessage } from "../types";

// =============================================================================
// Données d'exemple — UNIQUEMENT pour visualiser le design.
// -----------------------------------------------------------------------------
// Aucune de ces valeurs ne provient du back-end. Elles remplacent la sortie de
// `suggest_next_chord_from_audio()` et de la discussion RAG le temps que l'API
// soit branchée. Tu pourras supprimer ce fichier une fois le back-end prêt.
// =============================================================================

export const sampleAnalysis: Analysis = {
  fileName: "improvisation_session_01.mp3",
  durationLabel: "0:42",
  keyRoot: "C",
  keyMode: "majeur",
  confidence: 0.82,
  progression: [
    { degree: "I", chord: "C" },
    { degree: "VIm", chord: "Am" },
    { degree: "IV", chord: "F" },
  ],
  suggestion: {
    candidates: [
      { degree: "V", chord: "G" },
      { degree: "I", chord: "C" },
    ],
    rationale:
      "Séquence reconnue parmi les progressions de référence du moteur musical.",
  },
};

export const sampleMessages: ChatMessage[] = [
  {
    id: "m1",
    role: "assistant",
    content:
      "Bienvenue ! J'ai analysé votre enregistrement. Posez-moi vos questions sur la progression détectée, ou demandez-moi d'approfondir une suggestion.",
  },
  {
    id: "m2",
    role: "user",
    content:
      "J'ai joué I – VIm – IV en Do majeur. Que puis-je enchaîner et pourquoi ?",
  },
  {
    id: "m3",
    role: "assistant",
    content:
      "Votre boucle I – VIm – IV (Do – La mineur – Fa) est une progression pop très stable, qui installe la tonalité sans tension forte.\n\nPour conclure, l'enchaînement le plus attendu est V – I : le Sol majeur crée une dominante qui appelle naturellement le retour au Do. C'est la cadence parfaite, l'oreille la perçoit comme une « résolution ».\n\nQuelques variantes :\n• V → vi (Sol → La mineur) pour une cadence rompue, plus surprenante ;\n• IV → I pour une fin douce, sans dominante ;\n• V7 → I si vous voulez renforcer la tension avant la résolution.",
  },
];
