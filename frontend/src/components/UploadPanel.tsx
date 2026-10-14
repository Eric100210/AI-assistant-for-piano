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
    text: "Le moteur propose la suite, le RAG explique le pourquoi.",
  },
];

/**
 * Étape 1 — dépôt du fichier audio.
 *
 * ⚠️ STATIQUE : la zone de dépôt est purement décorative pour l'instant.
 * Pour la rendre fonctionnelle, tu brancheras un `<input type="file">` et un
 * appel `POST /analyze` (multipart/form-data) vers FastAPI.
 */
export function UploadPanel() {
  return (
    <Panel
      step="1"
      icon={<UploadCloud width={19} height={19} />}
      title="Importer un enregistrement"
      subtitle="Déposez un fichier audio pour lancer l'analyse."
      action={<span className={styles.formatBadge}>.mp3 · .wav · .m4a</span>}
    >
      <div className={styles.layout}>
        <div className={styles.dropzone} role="group" aria-label="Zone de dépôt audio">
          <span className={styles.dropIcon}>
            <UploadCloud width={24} height={24} />
          </span>
          <p className={styles.dropTitle}>
            Glissez votre fichier audio ici
          </p>
          <p className={styles.dropHint}>
            ou <span className={styles.fakeLink}>parcourez vos fichiers</span> — 25 Mo max.
          </p>
          <button type="button" className={styles.browseButton} disabled>
            Choisir un fichier
          </button>
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
