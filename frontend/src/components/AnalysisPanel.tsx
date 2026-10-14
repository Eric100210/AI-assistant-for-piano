import type { Analysis, ChordEvent } from "../types";
import { Activity, ArrowRight, Sparkles } from "./Icons";
import { Panel } from "./Panel";
import styles from "./AnalysisPanel.module.css";

interface AnalysisPanelProps {
  analysis: Analysis;
}

/** Étape 2 — restitution de l'analyse : tonalité, accords, suggestion. */
export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  const { keyRoot, keyMode, confidence, progression, suggestion } = analysis;
  const confidencePct = Math.round(confidence * 100);
  const [primary, ...alternatives] = suggestion.candidates;

  return (
    <Panel
      step="2"
      icon={<Activity width={19} height={19} />}
      title="Analyse"
      subtitle={`${analysis.fileName} · ${analysis.durationLabel}`}
      action={
        <span className={styles.confidenceBadge}>
          confiance {confidencePct}%
        </span>
      }
    >
      <div className={styles.stack}>
        {/* ----------------------------- Tonalité ----------------------------- */}
        <div className={styles.keyCard}>
          <div className={styles.keyGlow} />
          <div className={styles.keyInfo}>
            <span className={styles.keyLabel}>Tonalité détectée</span>
            <div className={styles.keyValue}>
              <span className={styles.keyRoot}>{keyRoot}</span>
              <span className={styles.keyMode}>{keyMode}</span>
            </div>
          </div>
          <div className={styles.confidence}>
            <span className={styles.confidenceValue}>{confidencePct}%</span>
            <span className={styles.confidenceLabel}>de certitude</span>
            <div className={styles.confidenceBar}>
              <span
                className={styles.confidenceFill}
                style={{ width: `${confidencePct}%` }}
              />
            </div>
          </div>
        </div>

        {/* --------------------------- Progression ---------------------------- */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>Progression détectée</span>
          <div className={styles.progression}>
            {progression.map((event, index) => (
              <ChordChip key={`${event.degree}-${index}`} event={event} index={index} />
            ))}
            <span className={styles.ellipsis} aria-hidden>
              ···
            </span>
          </div>
        </div>

        {/* ---------------------------- Suggestion ---------------------------- */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>Prochain accord suggéré</span>
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
                    Aucune suggestion évidente
                  </span>
                </div>
              )}
              {alternatives.length > 0 ? (
                <div className={styles.alternatives}>
                  <span className={styles.altLabel}>ou</span>
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
      </div>
    </Panel>
  );
}

function ChordChip({ event, index }: { event: ChordEvent; index: number }) {
  return (
    <>
      {index > 0 ? (
        <span className={styles.arrow} aria-hidden>
          <ArrowRight width={14} height={14} />
        </span>
      ) : null}
      <span className={styles.chordChip}>
        <span className={styles.chordDegree}>{event.degree}</span>
        <span className={styles.chordName}>{event.chord}</span>
      </span>
    </>
  );
}
