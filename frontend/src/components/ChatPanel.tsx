import type { ChatMessage } from "../types";
import { Book, Send, Sparkles } from "./Icons";
import { Panel } from "./Panel";
import styles from "./ChatPanel.module.css";

interface ChatPanelProps {
  messages: ChatMessage[];
}

/**
 * Étape 3 — conversation avec l'assistant théorique (RAG).
 *
 * ⚠️ STATIQUE : les messages viennent de `sample.ts` et l'envoi est désactivé.
 * Pour brancher : POST /chat avec { query, history } et afficher la réponse
 * (idéalement en streaming via SSE pour l'effet « réponse qui s'écrit »).
 */
export function ChatPanel({ messages }: ChatPanelProps) {
  return (
    <Panel
      className={styles.chatPanel}
      step="3"
      icon={<Book width={19} height={19} />}
      title="Assistant théorie"
      subtitle="Explications appuyées sur tes cours"
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
        </div>

        <form className={styles.composer} onSubmit={(event) => event.preventDefault()}>
          <textarea
            className={styles.input}
            rows={1}
            placeholder="Posez une question sur la progression…"
            disabled
            aria-label="Votre question"
          />
          <button type="submit" className={styles.send} disabled aria-label="Envoyer">
            <Send width={17} height={17} />
          </button>
        </form>
        <p className={styles.note}>
          Sera branché sur <code>POST /chat</code> (réponse en streaming).
        </p>
      </div>
    </Panel>
  );
}
