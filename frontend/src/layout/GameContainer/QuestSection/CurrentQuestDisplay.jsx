import React from 'react';
import styles from './CurrentQuestDisplay.module.scss';

export default function CurrentQuestDisplay({ quest }) {
  const { title = 'None', intro = 'No active quest yet...', outro = '' } = quest || {};

  return (
    <div className={styles.currentQuestSection}>
      <p className={`${styles.questText} ${styles.questLabel}`}>
        <strong>Current quest:</strong>{' '}
        <span className={styles.currentQuestTitle}>{title}</span>
      </p>
      <p className={styles.questText}>{intro}</p>
      {outro && <p className={styles.questText}>{outro}</p>}
    </div>
  );
}
