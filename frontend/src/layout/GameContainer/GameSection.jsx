import React from 'react';
import styles from './GameSection.module.scss';

export default function GameSection({
  type,
  status = 'empty',
  className = '',
  children,
}) {
  return (
    <div className={`${styles.gameSection} ${type}Section`}>
      {/* Header */}
      <div className={styles.sectionHeader}>
        <div className={styles.sectionStatus}>
          <span className={styles.sectionStatusHeader}>{type}:</span>
          <span className={styles.sectionStatusMessage}>{status}</span>
        </div>
      </div>

      {/* Body */}
      <div className={styles.sectionBody}>
        {children}
      </div>
    </div>
  );
}
