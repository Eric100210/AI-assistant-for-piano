import { useEffect, useRef, useState } from "react";

import type { Analysis, DetectedChord } from "../types";
import { Activity, ArrowRight, Check, Copy, Sparkles } from "./Icons";
import { Panel } from "./Panel";
import styles from "./AnalysisPanel.module.css";

interface AnalysisPanelProps {
  analysis: Analysis;
  file: File;
}

/** Étape 2 — restitution de l'analyse : suggestion, accords, tonalité. */
export function AnalysisPanel({ analysis, file }: AnalysisPanelProps): JSX.Element {
  const { keyRoot, keyMode, keyStatus, alternativeKey, progression, suggestion } = analysis;
  const audioRef = useRef<HTMLAudioElement>(null);
  const [audioUrl, setAudioUrl] = useState<string>();
  const [duration, setDuration] = useState<number>();
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackError, setPlaybackError] = useState<string>();

  useEffect(() => {
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function playFrom(start: number): void {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.min(start, audio.duration);
    setCurrentTime(audio.currentTime);
    setPlaybackError(undefined);
    void audio.play().catch((error: unknown) => {
      if (!(error instanceof DOMException && error.name === "AbortError")) {
        setPlaybackError("Playback could not start. Try the audio controls.");
      }
    });
  }
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
      subtitle={duration === undefined ? analysis.fileName : `${analysis.fileName} · ${formatTime(duration)}`}
    >
      <div className={styles.stack}>
        {/* ---------------------------- Suggestion ---------------------------- */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>Suggested next chord</span>
          <div className={styles.suggestion}>
            {suggestion.candidates.length ? (
              <ol className={styles.candidates}>
                {suggestion.candidates.map((candidate) => (
                  <li key={candidate.degree} className={styles.candidate}>
                    <span><b>{candidate.chord}</b> · {candidate.degree}</span>
                    <span className={styles.candidateEvidence}>
                      {candidate.referenceMatches} {candidate.referenceMatches === 1 ? "reference" : "references"}
                      {candidate.example.length > 0 ? ` · ${candidate.example.join(" – ")}` : ""}
                    </span>
                  </li>
                ))}
              </ol>
            ) : (
              <div className={styles.suggestionHead}>
                <Sparkles width={16} height={16} />
                <span>No suggested chord</span>
              </div>
            )}
            <p className={styles.rationale}>{suggestion.rationale}</p>
          </div>
        </div>

        {/* --------------------------- Progression ---------------------------- */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>Detected progression</span>
          <audio
            ref={audioRef}
            className={styles.player}
            src={audioUrl}
            controls
            preload="metadata"
            aria-label="Listen to your recording"
            onDurationChange={(event) => {
              const seconds = event.currentTarget.duration;
              setDuration(Number.isFinite(seconds) ? seconds : undefined);
            }}
            onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
            onError={() => setPlaybackError("This audio format could not be played in your browser.")}
          />
          {playbackError ? <p role="status" className={styles.keyMode}>{playbackError}</p> : null}
          {progression.length > 0 && duration !== undefined && (
            <span className={styles.keyMode}>Select a chord to listen from its timestamp.</span>
          )}
          <div className={styles.progression}>
            {progression.map((event, index) => (
              <ChordChip
                key={`${event.start}-${index}`}
                event={event}
                index={index}
                active={currentTime >= event.start && currentTime < event.end}
                canPlay={duration !== undefined}
                onPlay={playFrom}
              />
            ))}
            {progression.length === 0 ? <span>No chords detected</span> : null}
          </div>
        </div>

        {/* ----------------------------- Tonalité ----------------------------- */}
        <div className={styles.keyCard}>
          <div className={styles.keyGlow} />
          <div className={styles.keyInfo}>
            <span className={styles.keyLabel}>{keyStatus === "tentative" ? "Tentative key" : "Estimated key"}</span>
            <div className={styles.keyValue}>
              <span className={styles.keyRoot}>{keyRoot ?? "Undetermined"}</span>
              <span className={styles.keyMode}>{keyMode}</span>
            </div>
            {keyStatus === "tentative" && (
              <span className={styles.keyMode}>
                {alternativeKey ? `Also plausible: ${alternativeKey}` : "Limited tonal evidence"}
              </span>
            )}
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

function formatTime(seconds: number): string {
  const tenths = Math.floor(seconds * 10 + 1e-6);
  const minutes = Math.floor(tenths / 600);
  const remainder = ((tenths % 600) / 10).toFixed(1).padStart(4, "0");
  return `${minutes}:${remainder}`;
}

interface ChordChipProps {
  event: DetectedChord;
  index: number;
  active: boolean;
  canPlay: boolean;
  onPlay: (start: number) => void;
}

function ChordChip({ event, index, active, canPlay, onPlay }: ChordChipProps): JSX.Element {
  return (
    <>
      {index > 0 ? (
        <span className={styles.arrow} aria-hidden>
          <ArrowRight width={14} height={14} />
        </span>
      ) : null}
      <button
        type="button"
        className={styles.chordChip}
        disabled={!canPlay}
        aria-current={active || undefined}
        onClick={() => onPlay(event.start)}
      >
        {event.degree ? <span className={styles.chordDegree}>{event.degree}</span> : null}
        <span className={styles.chordName}>{event.chord}</span>
        <span className={styles.chordTime}>{formatTime(event.start)}–{formatTime(event.end)}</span>
      </button>
    </>
  );
}
