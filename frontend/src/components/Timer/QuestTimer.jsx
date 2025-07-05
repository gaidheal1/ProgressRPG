import React, { useEffect, useState, useMemo } from 'react';
import { useGame } from '../../context/GameContext';
import styles from './QuestTimer.module.scss';
import { formatDuration } from '../../../utils/formatUtils.js';
import TimerDisplay from './TimerDisplay.jsx';
import List from '../List/List.jsx';


export default function QuestTimer() {
  const { questTimer } = useGame();
  const { subject: quest, status, duration, elapsed, remainingTime } = questTimer;
  const displayTime = formatDuration(remainingTime);
  const { name = 'None', intro_text = 'No active quest yet...', outro_text = '', stages } = quest || {};

  function shuffle(array) {
    return array.sort(() => Math.random() - 0.5);
  }

  let stageDuration = 3
  const maxStages = Math.floor(duration / stageDuration);

  // If there aren't enough stages given stageDuration, divide quest duration into number of stages
  if (maxStages > stages.length) {
    stageDuration = Math.floor(duration / stages.length);
  }
  const shuffledStages = useMemo(() => shuffle([...stages]), []);
  const questStages = shuffledStages.slice(0, maxStages);
  const currentStageIndex = Math.floor(elapsed / stageDuration);

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
          items={questStages}
          renderItem={(stage, index) => {

            const isCurrent = index === currentStageIndex;
            const isCompleted = index < currentStageIndex;

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
