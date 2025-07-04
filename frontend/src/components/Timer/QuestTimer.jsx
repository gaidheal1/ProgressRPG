import React, { useEffect, useState } from 'react';
import { useGame } from '../../context/GameContext';
import styles from './QuestTimer.module.scss';
import { formatDuration } from '../../../utils/formatUtils.js';
import TimerDisplay from './TimerDisplay.jsx';
import List from '../List/List.jsx';


export default function QuestTimer() {
  const { questTimer } = useGame();
  const { subject: quest, status, elapsed, remainingTime } = questTimer;
  const displayTime = formatDuration(remainingTime);
  const { name = 'None', intro_text = 'No active quest yet...', outro_text = '', stages } = quest || {};

  console.log('Stages:', stages);
  console.log('Elapsed:', elapsed);

  return (
    <div className={styles.questRow}>
      <TimerDisplay
        label="Quest"
        status={status}
        time={displayTime}
      />

      <div className={styles.currentQuestSection}>
        <p className={styles.questText}>
          <span className={styles.questLabel}>Current quest:{' '}</span>
          <span className={styles.currentQuestTitle}>{name}</span>
        </p>
        <p className={styles.questText}>{intro_text}</p>

        <List
          items={stages}
          renderItem={(stage, index) => {
            const isCompleted = stage.endTime <= elapsed;
            const isCurrent = elapsed < stage.endTime && (
              index === 0 || elapsed >= stages[index - 1].endTime
            );

            let className;
            if (isCompleted) className = styles.completedStage;
            else if (isCurrent) className = styles.currentStage;
            else className = styles.futureStage;

            return <div className={className}>{stage.text}</div>;
          }}
          className={styles.list}
          sectionClass={styles.listSection}
        />

        <p
          className={styles.questText}
          style={{ display: status=="complete" ? 'flex' : 'none' }}
        >{outro_text}</p>
      </div>

    </div>
  );
}
