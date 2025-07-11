import React from 'react';
import styles from './Infobox.module.scss';
import ProgressBar from '../../../components/ProgressBar/ProgressBar';

function getRows(data, type) {
  if (!data) return [];

  if (type === 'player') {
    return [
      { label: 'Player', value: data.name },
      { label: 'Level', value: data.level },
      // { label: 'XP', value: `${data.xp}/${data.xp_next_level}` },
    ];
  }

  if (type === 'character') {
    return [
      { label: 'Character', value: data.first_name },
      { label: 'Level', value: data.level },
      // { label: 'XP', value: `${data.xp}/${data.xp_next_level}` },
    ];
  }

  return [];
}


function getCustomClasses(label) {
  switch (label.toLowerCase()) {
    case 'level':
      return { labelClass: styles.levelLabel, valueClass: styles.levelValue };
    case 'xp':
      return { labelClass: styles.xpLabel, valueClass: styles.xpValue };
    case 'player':
    case 'character':
      return { labelClass: styles.nameLabel, valueClass: styles.nameValue };
    default:
      return { labelClass: '', valueClass: '' };
  }
}


export default function Infobox({ title, type, data }) {
  const rows = getRows(data, type);


  return (
    <div className={styles.infoBox}>
      {title && <div className={styles.title}>{title}</div>}
      <div className={styles.columns}>
        <div className={styles.column}>
          {rows.map(({ label, value }, i) => {
            const { labelClass, valueClass } = getCustomClasses(label);
            return (
              <div key={i} className={styles.row}>
                <span className={`${styles.label} ${labelClass}`}>{label}:</span>
                <span className={`${styles.value} ${valueClass}`}>{value}</span>
              </div>
            );
          })}
          <ProgressBar
            value={data.xp}
            max={data.xp_next_level}
            label={`XP: ${data.xp} / ${data.xp_next_level}`}
            color="xp"  // Use your CSS class for XP color, define in ProgressBar.module.scss
          />
        </div>
      </div>
    </div>
  );
}
