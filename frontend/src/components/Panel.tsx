import type { ReactNode } from "react";

import styles from "./Panel.module.css";

interface PanelProps {
  /** Numéro d'étape affiché à côté du titre (ex. "1"). */
  step?: string;
  title: string;
  subtitle?: string;
  /** Icône affichée dans une pastille à gauche du titre. */
  icon?: ReactNode;
  /** Contenu optionnel aligné à droite de l'en-tête (badge, bouton…). */
  action?: ReactNode;
  /** Contenu principal. */
  children: ReactNode;
  className?: string;
}

/** Carte de section réutilisable, socle visuel de l'application. */
export function Panel({
  step,
  title,
  subtitle,
  icon,
  action,
  children,
  className,
}: PanelProps) {
  return (
    <section className={[styles.panel, className].filter(Boolean).join(" ")}>
      <header className={styles.header}>
        <div className={styles.heading}>
          {icon ? <span className={styles.icon}>{icon}</span> : null}
          <div className={styles.titles}>
            <div className={styles.titleRow}>
              {step ? <span className={styles.step}>{step}</span> : null}
              <h2 className={styles.title}>{title}</h2>
            </div>
            {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}
          </div>
        </div>
        {action ? <div className={styles.action}>{action}</div> : null}
      </header>
      <div className={styles.body}>{children}</div>
    </section>
  );
}
