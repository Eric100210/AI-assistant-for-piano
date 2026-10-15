import { useEffect, useRef, useState } from "react";

import type { ChatMessage } from "../types";
import { Book, Send, Sparkles } from "./Icons";
import { Panel } from "./Panel";
import styles from "./ChatPanel.module.css";

interface ChatPanelProps {
  messages: ChatMessage[];
  /** Appelé à l'envoi d'une question à l'assistant RAG (`POST /api/chat`). */
  onSend: (query: string) => void;
  /** Vrai pendant que l'assistant « réfléchit ». */
  isThinking: boolean;
}

/** Étape 3 — conversation avec l'assistant musical (RAG). */
export function ChatPanel({ messages, onSend, isThinking }: ChatPanelProps) {
  const [value, setValue] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isThinking]);

  function submit() {
    const query = value.trim();
    if (!query || isThinking) return;
    onSend(query);
    setValue("");
  }

  return (
    <Panel
      className={styles.chatPanel}
      step="3"
      icon={<Book width={19} height={19} />}
      title="Assistant MusAIc"
      subtitle="Explications appuyées sur la théorie musicale"
      action={<span className={styles.ragBadge}>RAG</span>}
    >
      <div className={styles.chat}>
        <div className={styles.messages}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${
                message.role === "user" ? styles.user : styles.assistant
              }`}
            >
              <span className={styles.avatar}>
                {message.role === "assistant" ? (
                  <Sparkles width={15} height={15} />
                ) : (
                  "Moi"
                )}
              </span>
              <div className={styles.bubble}>
                <p className={styles.text}>{message.content}</p>
              </div>
            </div>
          ))}

          {isThinking ? (
            <div className={`${styles.message} ${styles.assistant}`}>
              <span className={styles.avatar}>
                <Sparkles width={15} height={15} />
              </span>
              <div className={`${styles.bubble} ${styles.typingBubble}`}>
                <span className={styles.typingDot} />
                <span className={styles.typingDot} />
                <span className={styles.typingDot} />
              </div>
            </div>
          ) : null}

          <div ref={endRef} />
        </div>

        <form
          className={styles.composer}
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
        >
          <textarea
            className={styles.input}
            rows={1}
            placeholder="Posez une question sur la progression…"
            aria-label="Votre question"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                submit();
              }
            }}
          />
          <button
            type="submit"
            className={styles.send}
            disabled={isThinking || value.trim().length === 0}
            aria-label="Envoyer"
          >
            <Send width={17} height={17} />
          </button>
        </form>
        <p className={styles.note}>
          Réponses générées par le RAG local (Ollama).
        </p>
      </div>
    </Panel>
  );
}
