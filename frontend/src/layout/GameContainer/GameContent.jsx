import React from 'react';
import ActivitySection from './ActivitySection/ActivitySection';
import QuestSection from './QuestSection/QuestSection';
import styles from './GameContent.module.scss';
import { TimerProvider } from '../../context/TimerContext';

export default function GameContent() {

  return (
    <div className={styles.gameContent}>
      <TimerProvider>
        <ActivitySection />
        <QuestSection />
      </TimerProvider>
    </div>
  );
}
