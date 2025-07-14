import React from 'react';
import styles from './GameSection.module.scss';

export default function GameSection({ type, children }) {
  return (
    <div className={`${styles.gameSection} ${type}Section`}>
      {/* Header */}
      <div className={styles.sectionHeader}>
        <div className={styles.sectionStatus}>
          <span className={styles.sectionStatusHeader}>{type}</span>
        </div>
      </div>

      {/* Body */}
      <div className={styles.sectionBody}>
        {children}
      </div>
    </div>
  );
}
