import { LogoMark } from "./Icons";
import styles from "./AppHeader.module.css";

/** En-tête fixe : marque, badge de statut et modèle utilisé. */
export function AppHeader() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <a className={styles.brand} href="/" aria-label="Accueil MusAIc">
          <span className={styles.logo}>
            <LogoMark width={22} height={22} />
          </span>
          <span className={styles.brandText}>
            <span className={styles.wordmark}>MusAIc</span>
            <span className={styles.tagline}>Piano &amp; théorie assistés</span>
          </span>
        </a>

        <div className={styles.meta}>
          <span className={`${styles.badge} ${styles.badgeLocal}`}>
            <span className={styles.dot} />
            Aperçu statique
          </span>
          <span className={styles.badge}>llama3.2:3b · Ollama</span>
        </div>
      </div>
    </header>
  );
}
