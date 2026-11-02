import type { ReactNode } from "react";

import styles from "./Panel.module.css";

interface PanelProps {
  /** Step number displayed next to the title (e.g. "1"). */
  step?: string;
  title: string;
  subtitle?: string;
  /** Icon displayed in a pill to the left of the title. */
  icon?: ReactNode;
  /** Optional content aligned to the right of the header (badge, button…). */
  action?: ReactNode;
  /** Main content. */
  children: ReactNode;
  className?: string;
}

/** Reusable section card that forms the visual foundation of the app. */
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
