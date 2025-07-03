import React from 'react';
import { useGame } from '../../context/GameContext';
import styles from './QuestTimer.module.scss';
import sharedStyles from './Timer.module.scss';
import { formatDuration } from '../../../utils/formatUtils.js';

export default function QuestTimer() {
  const { questTimer } = useGame();
  const { subject: quest, status, remainingTime } = questTimer;
  const displayTime = formatDuration(remainingTime);
  const { title = 'None', intro = 'No active quest yet...', outro = '' } = quest || {};

  return (
    <div className={styles.timer}>
      <p className={`${styles.questText} ${styles.questLabel}`}>
        <strong>Current quest:</strong>{' '}
        <span className={styles.currentQuestTitle}>{title}</span>
      </p>
      <p className={styles.questText}>{intro}</p>
      <p className={styles.questText}>{outro}</p>

      <div className={sharedStyles.timerFrame}>
        <div className={sharedStyles.timerText}>{displayTime}</div>
        <div className={styles.timerStatus}>Status: {status}</div>
      </div>
    </div>
  );
}
