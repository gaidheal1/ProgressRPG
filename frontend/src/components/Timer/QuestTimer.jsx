import React, { useEffect, useState, useMemo } from 'react';
import { useGame } from '../../context/GameContext';
import styles from './QuestTimer.module.scss';
import { formatDuration } from '../../../utils/formatUtils.js';
import TimerDisplay from './TimerDisplay.jsx';
import List from '../List/List.jsx';


function shuffle(array) {
  return array.sort(() => Math.random() - 0.5);
}

export default function QuestTimer() {
  const { questTimer } = useGame();
  const { subject: quest, status, duration, elapsed, remaining, processedStages, globalStageIndex } = questTimer;
  const displayTime = formatDuration(remaining);
  const { name = 'None', intro_text = 'No active quest yet...', outro_text = '' } = quest || {};

  console.log(`[Quest Timer] processedStages: ${processedStages}`);
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
          items={processedStages}
          renderItem={({ stage, globalIndex }, index) => {

            const isCompleted = globalIndex < globalStageIndex;
            const isCurrent = globalIndex === globalStageIndex;
            const isFuture = globalIndex > globalStageIndex;

            let className;
            if (isCompleted) className = styles.completedStage;
            else if (isCurrent) className = styles.currentStage;
            else className = styles.futureStage;

            return <div className={className} key={index}>{stage.text}</div>;
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
