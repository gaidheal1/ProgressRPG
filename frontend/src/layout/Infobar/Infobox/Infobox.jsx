import React from 'react';
import styles from './Infobox.module.scss';

export default function Infobox({ title, columns = [] }) {
  return (
    <div className={styles.infoBox}>
      {/* {title && <h2 className={styles.heading}>{title}</h2>} */}
      <div className={styles.columns}>
        {columns.map((col, i) => (
          <div key={i} className={styles.column}>
            {col.map(({ label, value }, j) => (
              <div key={j} className={styles.row}>
                <span className={styles.label}>{label}:</span>
                <span className={styles.value}>{value}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
