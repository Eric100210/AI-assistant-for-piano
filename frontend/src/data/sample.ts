import type { Analysis, ChordEvent } from "../types";

// =============================================================================
// Données d'exemple — UNIQUEMENT pour visualiser le design tant que le
// back-end n'est pas branché. Tu pourras supprimer ce fichier une fois les
// appels réels en place dans `src/api/client.ts`.
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

/** Explication d'exemple renvoyée par le chat (mock). */
export const sampleExplanation =
  "Votre boucle I – VIm – IV (Do – La mineur – Fa) est une progression pop très stable, qui installe la tonalité sans tension forte.\n\n" +
  "Pour conclure, l'enchaînement le plus attendu est V – I : le Sol majeur crée une dominante qui appelle naturellement le retour au Do. C'est la cadence parfaite, l'oreille la perçoit comme une « résolution ».\n\n" +
  "Quelques variantes :\n" +
  "• V → vi (Sol → La mineur) pour une cadence rompue, plus surprenante ;\n" +
  "• IV → I pour une fin douce, sans dominante ;\n" +
  "• V7 → I si vous voulez renforcer la tension avant la résolution.";

/** Un petit raccourci pour construire un ChordEvent (pratique dans les mocks). */
export function chord(degree: string, name: string): ChordEvent {
  return { degree, chord: name };
}
