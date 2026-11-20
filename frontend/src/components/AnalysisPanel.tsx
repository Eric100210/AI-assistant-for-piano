import { useEffect, useState } from "react";

import type { Analysis, DetectedChord } from "../types";
import { Activity, ArrowRight, Check, Copy, Sparkles } from "./Icons";
import { Panel } from "./Panel";
import styles from "./AnalysisPanel.module.css";

interface AnalysisPanelProps {
  analysis: Analysis;
}

/** Étape 2 — restitution de l'analyse : suggestion, accords, tonalité. */
export function AnalysisPanel({ analysis }: AnalysisPanelProps): JSX.Element {
  const { keyRoot, keyMode, progression, suggestion } = analysis;
  const [primary, ...alternatives] = suggestion.candidates;
  const [copied, setCopied] = useState(false);

  // Retour visuel « Copié ! » pendant 2 s, annulé si le composant est démonté.
  useEffect(() => {
    if (!copied) return;
    const id = window.setTimeout(() => setCopied(false), 2000);
    return () => window.clearTimeout(id);
  }, [copied]);

  async function copyProgression(): Promise<void> {
    await copyText(formatProgression(analysis));
    setCopied(true);
  }

  return (
    <Panel
      step="2"
      icon={<Activity width={19} height={19} />}
      title="Analysis"
      subtitle={analysis.fileName}
    >
      <div className={styles.stack}>
        {/* ---------------------------- Suggestion ---------------------------- */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>Suggested next chord</span>
          <div className={styles.suggestion}>
            <div className={styles.suggestionHead}>
              <span className={styles.suggestionIcon}>
                <Sparkles width={16} height={16} />
              </span>
              {primary ? (
                <div className={styles.primaryCandidate}>
                  <span className={styles.primaryDegree}>{primary.degree}</span>
                  <span className={styles.primaryChord}>{primary.chord}</span>
                </div>
              ) : (
                <div className={styles.primaryCandidate}>
                  <span className={styles.primaryChord}>
                    No obvious suggestion
                  </span>
                </div>
              )}
              {alternatives.length > 0 ? (
                <div className={styles.alternatives}>
                  <span className={styles.altLabel}>or</span>
                  {alternatives.map((alt) => (
                    <span key={alt.degree} className={styles.altChip}>
                      <b>{alt.degree}</b>
                      <span>{alt.chord}</span>
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
            <p className={styles.rationale}>{suggestion.rationale}</p>
          </div>
        </div>

        {/* --------------------------- Progression ---------------------------- */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>Detected progression</span>
          <div className={styles.progression}>
            {progression.map((event, index) => (
              <ChordChip key={`${event.degree}-${index}`} event={event} index={index} />
            ))}
            {progression.length === 0 ? <span>No chords detected</span> : null}
          </div>
        </div>

        {/* ----------------------------- Tonalité ----------------------------- */}
        <div className={styles.keyCard}>
          <div className={styles.keyGlow} />
          <div className={styles.keyInfo}>
            <span className={styles.keyLabel}>Detected key</span>
            <div className={styles.keyValue}>
              <span className={styles.keyRoot}>{keyRoot ?? "Undetermined"}</span>
              <span className={styles.keyMode}>{keyMode}</span>
            </div>
          </div>
        </div>

        {/* --------------------------- Copier la progression ------------------ */}
        <div className={styles.copyRow}>
          <button
            type="button"
            className={`${styles.copyButton} ${copied ? styles.copied : ""}`}
            onClick={copyProgression}
            disabled={progression.length === 0}
          >
            {copied ? (
              <Check width={15} height={15} />
            ) : (
              <Copy width={15} height={15} />
            )}
            {copied ? "Copied" : "Copy progression"}
          </button>
        </div>
      </div>
    </Panel>
  );
}

/** Met en forme la progression pour le presse-papiers (lisible par l'assistant). */
function formatProgression(analysis: Analysis): string {
  const progression = analysis.progression
    .map(({ chord, degree }) => degree ? `${chord} (${degree})` : chord)
    .join(" – ");
  const key = analysis.keyRoot ? ` in ${analysis.keyRoot} ${analysis.keyMode}` : "";
  return `I played ${progression}${key}.`;
}

/** Copie un texte dans le presse-papiers, avec un repli pour les contextes non sécurisés. */
async function copyText(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    document.body.removeChild(area);
  }
}

function ChordChip({ event, index }: { event: DetectedChord; index: number }): JSX.Element {
  return (
    <>
      {index > 0 ? (
        <span className={styles.arrow} aria-hidden>
          <ArrowRight width={14} height={14} />
        </span>
      ) : null}
      <span
        className={styles.chordChip}
        title={`${event.start.toFixed(1)}–${event.end.toFixed(1)} s`}
      >
        {event.degree ? <span className={styles.chordDegree}>{event.degree}</span> : null}
        <span className={styles.chordName}>{event.chord}</span>
      </span>
    </>
  );
}
