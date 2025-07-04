// components/TimerDisplay/TimerDisplay.jsx
import React from 'react';
import styles from './TimerDisplay.module.scss'; // local styles

export default function TimerDisplay({ label = 'Timer', time = '00:00', status }) {
  return (
    <div className={styles.timerFrame}>
      <div className={styles.timerStatus}>
        {label}: {status}
      </div>
      <div className={styles.timerText}>
        {time}
      </div>
    </div>
  );
}
