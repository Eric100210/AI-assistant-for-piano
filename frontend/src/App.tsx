import { useRef, useState } from "react";

import { analyzeAudio, sendMessage } from "./api/client";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { AnalyzingPanel } from "./components/AnalyzingPanel";
import { AppHeader } from "./components/AppHeader";
import { ChatPanel } from "./components/ChatPanel";
import { UploadPanel } from "./components/UploadPanel";
import type { Analysis, ChatMessage } from "./types";
import styles from "./App.module.css";

let messageCounter = 0;
function nextMessageId(): string {
  messageCounter += 1;
  return `m-${messageCounter}`;
}

function welcomeMessage(analysis: Analysis): ChatMessage {
  return {
    id: nextMessageId(),
    role: "assistant",
    content: `I analyzed “${analysis.fileName}”: the key is ${analysis.keyRoot} ${analysis.keyMode}. Ask me anything about this progression or what could come next.`,
  };
}

/**
 * Point d'entrée de l'interface.
 *
 * Le parcours : tant qu'aucun fichier n'est déposé, seuls le hero et la zone
 * d'import sont affichés. Dès qu'un audio est choisi, on lance l'analyse puis
 * on révèle les panneaux « Analyse » et « Assistant MusAIc ».
 *
 * Les appels réseau passent par `src/api/client.ts` (API FastAPI, proxyfée par
 * le serveur de dev Vite sur `/api`).
 */
export default function App() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const workspaceRef = useRef<HTMLDivElement>(null);

  async function handleFileSelected(file: File) {
    setError(null);
    setSelectedFileName(file.name);
    setAnalysis(null);
    setMessages([]);
    setIsAnalyzing(true);

    try {
      const result = await analyzeAudio(file);
      setAnalysis(result);
      setMessages([welcomeMessage(result)]);
      // Amène l'utilisateur vers les résultats une fois le DOM mis à jour.
      requestAnimationFrame(() =>
        workspaceRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleSend(query: string) {
    setMessages((previous) => [
      ...previous,
      { id: nextMessageId(), role: "user", content: query },
    ]);
    setIsThinking(true);

    try {
      const reply = await sendMessage(query, messages);
      setMessages((previous) => [
        ...previous,
        { id: nextMessageId(), role: "assistant", content: reply },
      ]);
    } catch {
      setMessages((previous) => [
        ...previous,
        {
          id: nextMessageId(),
          role: "assistant",
          content: "The assistant is temporarily unavailable.",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  }

  function handleReset() {
    setAnalysis(null);
    setMessages([]);
    setSelectedFileName(null);
    setError(null);
    setIsAnalyzing(false);
  }

  return (
    <div className={styles.app}>
      <AppHeader />

      <main className={styles.main}>
        <section className={styles.hero}>
          <h1 className={styles.title}>
            MusAIc: your piano improvisation assistant
          </h1>
          <p className={styles.subtitle}>
            A short piano clip is enough. MusAIc detects the key and chords, suggests the
            most natural continuation, and discusses it with you.
          </p>

          <ul className={styles.features}>
            <li className={styles.feature}>Key</li>
            <li className={styles.feature}>Chords</li>
            <li className={styles.feature}>Next chords</li>
            <li className={styles.feature}>Direct chat</li>
          </ul>
        </section>

        <UploadPanel
          onFileSelected={handleFileSelected}
          selectedFileName={selectedFileName}
          isAnalyzing={isAnalyzing}
          onReset={handleReset}
        />

        {error ? <p className={styles.error}>{error}</p> : null}

        {isAnalyzing ? <AnalyzingPanel /> : null}

        {analysis ? (
          <div ref={workspaceRef} className={styles.workspace}>
            <AnalysisPanel analysis={analysis} />
            <ChatPanel messages={messages} onSend={handleSend} isThinking={isThinking} />
          </div>
        ) : null}
      </main>

      <footer className={styles.footer}>
        <span>MusAIc</span>
        <span className={styles.footerDot} />
        <span>ericdesaintchamas@gmail.com</span>
      </footer>
    </div>
  );
}
