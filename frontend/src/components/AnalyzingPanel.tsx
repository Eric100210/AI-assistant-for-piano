import { Activity } from "./Icons";
import { Panel } from "./Panel";
import styles from "./AnalyzingPanel.module.css";

/** Panneau de chargement affiché pendant l'analyse du fichier audio. */
export function AnalyzingPanel() {
  return (
    <Panel
      step="2"
      icon={<Activity width={19} height={19} />}
      title="Analyse en cours"
      subtitle="Transcription, reconnaissance des accords, recherche de la suite…"
    >
      <div className={styles.loading}>
        <span className={styles.spinner} aria-hidden />
        <div className={styles.skeleton} aria-hidden>
          <span className={styles.barWide} />
          <span className={styles.bar} />
          <span className={styles.barShort} />
        </div>
      </div>
    </Panel>
  );
}
