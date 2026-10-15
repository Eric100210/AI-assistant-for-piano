import { useRef, useState } from "react";

import { Activity, Music, UploadCloud, Wand } from "./Icons";
import { Panel } from "./Panel";
import styles from "./UploadPanel.module.css";

const PIPELINE = [
  {
    icon: <Music width={16} height={16} />,
    title: "Transcription MIDI",
    text: "Les notes jouées sont extraites de l'audio (modèle Basic Pitch).",
  },
  {
    icon: <Activity width={16} height={16} />,
    title: "Tonalité & accords",
    text: "La tonalité est détectée, puis chaque accord est reconnu.",
  },
  {
    icon: <Wand width={16} height={16} />,
    title: "Suggestion & théorie",
    text: "Le moteur propose la suite, l'assistant peut vous expliquer le pourquoi.",
  },
];

const ACCEPTED_FORMATS = ".mp3,.wav,.m4a,.flac,.ogg,audio/*";

interface UploadPanelProps {
  /** Appelé quand l'utilisateur dépose ou sélectionne un fichier. */
  onFileSelected: (file: File) => void;
  /** Nom du fichier actuellement analysé (ou `null`). */
  selectedFileName: string | null;
  /** Vrai pendant l'analyse (désactive la zone). */
  isAnalyzing: boolean;
  /** Réinitialise l'écran pour repartir de zéro. */
  onReset: () => void;
}

/** Étape 1 — dépôt / sélection du fichier audio. */
export function UploadPanel({
  onFileSelected,
  selectedFileName,
  isAnalyzing,
  onReset,
}: UploadPanelProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function openPicker() {
    if (!isAnalyzing) inputRef.current?.click();
  }

  function accept(file: File | null | undefined) {
    if (file && !isAnalyzing) onFileSelected(file);
  }

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    accept(event.dataTransfer.files?.[0]);
  }

  return (
    <Panel
      step="1"
      icon={<UploadCloud width={19} height={19} />}
      title="Importer un enregistrement"
      subtitle="Déposez un fichier audio pour lancer l'analyse."
      action={<span className={styles.formatBadge}>.mp3 · .wav · .m4a</span>}
    >
      <div className={styles.layout}>
        <div
          className={`${styles.dropzone} ${isDragging ? styles.dragging : ""} ${
            isAnalyzing ? styles.disabled : ""
          }`}
          role="button"
          tabIndex={0}
          aria-label="Déposer ou choisir un fichier audio"
          onClick={openPicker}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              openPicker();
            }
          }}
          onDragOver={(event) => {
            event.preventDefault();
            if (!isAnalyzing) setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_FORMATS}
            hidden
            onChange={(event) => {
              accept(event.target.files?.[0]);
              event.target.value = ""; // permet de re-sélectionner le même fichier
            }}
          />

          {selectedFileName ? (
            <>
              <span className={styles.fileIcon}>
                <Music width={24} height={24} />
              </span>
              <p className={styles.dropTitle}>{selectedFileName}</p>
              <p className={styles.dropHint}>
                {isAnalyzing ? "Analyse en cours…" : "Cliquez pour choisir un autre fichier."}
              </p>
              <button
                type="button"
                className={styles.browseButton}
                disabled={isAnalyzing}
                onClick={(event) => {
                  event.stopPropagation();
                  onReset();
                }}
              >
                Réinitialiser
              </button>
            </>
          ) : (
            <>
              <span className={styles.dropIcon}>
                <UploadCloud width={24} height={24} />
              </span>
              <p className={styles.dropTitle}>Glissez votre fichier audio ici</p>
              <p className={styles.dropHint}>
                ou <span className={styles.fakeLink}>parcourez vos fichiers</span> — 25 Mo max.
              </p>
              <button
                type="button"
                className={styles.browseButton}
                onClick={(event) => {
                  event.stopPropagation();
                  openPicker();
                }}
              >
                Choisir un fichier
              </button>
            </>
          )}
        </div>

        <ol className={styles.pipeline}>
          {PIPELINE.map((step, index) => (
            <li key={step.title} className={styles.pipelineItem}>
              <span className={styles.pipelineIcon}>{step.icon}</span>
              <div className={styles.pipelineText}>
                <span className={styles.pipelineTitle}>
                  <span className={styles.pipelineIndex}>{index + 1}</span>
                  {step.title}
                </span>
                <span className={styles.pipelineDesc}>{step.text}</span>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </Panel>
  );
}
