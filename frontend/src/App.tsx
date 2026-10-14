import { AnalysisPanel } from "./components/AnalysisPanel";
import { AppHeader } from "./components/AppHeader";
import { ChatPanel } from "./components/ChatPanel";
import { UploadPanel } from "./components/UploadPanel";
import { sampleAnalysis, sampleMessages } from "./data/sample";
import styles from "./App.module.css";

/**
 * Point d'entrée de l'interface.
 *
 * ⚠️ Ce front est volontairement STATIQUE : aucune interaction n'est branchée.
 * Les données affichées viennent de `src/data/sample.ts`.
 *
 * Pour brancher le back-end FastAPI :
 *   1. remplacer `sampleAnalysis` par le résultat d'un POST vers /analyze
 *      (upload du fichier audio) ;
 *   2. remplacer `sampleMessages` par l'état local de la conversation alimenté
 *      par POST /chat ;
 *   3. passer ces données en `props` aux composants (ils sont déjà prêts).
 */
export default function App() {
  return (
    <div className={styles.app}>
      <AppHeader />

      <main className={styles.main}>
        <section className={styles.hero}>
          <span className={styles.eyebrow}>Assistant d'improvisation &amp; de composition</span>
          <h1 className={styles.title}>
            Votre oreille, <span className={styles.gradient}>augmentée</span>.
          </h1>
          <p className={styles.subtitle}>
            Déposez un enregistrement de votre jeu : MusAIc identifie la tonalité et les
            accords, propose la suite la plus naturelle, puis vous explique la théorie
            derrière chaque choix.
          </p>

          <ul className={styles.features}>
            <li className={styles.feature}>Détection de la tonalité</li>
            <li className={styles.feature}>Reconnaissance des accords</li>
            <li className={styles.feature}>Suggestion du prochain accord</li>
            <li className={styles.feature}>Explications théoriques (RAG)</li>
          </ul>
        </section>

        <UploadPanel />

        <div className={styles.workspace}>
          <AnalysisPanel analysis={sampleAnalysis} />
          <ChatPanel messages={sampleMessages} />
        </div>
      </main>

      <footer className={styles.footer}>
        <span>MusAIc — analyse audio &amp; RAG de théorie musicale</span>
        <span className={styles.footerDot} />
        <span>Front en aperçu statique · API à brancher</span>
      </footer>
    </div>
  );
}
