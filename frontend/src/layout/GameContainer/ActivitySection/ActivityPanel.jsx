import React from 'react';
import List from '../../../components/List/List';
import styles from './ActivityPanel.module.scss';
import { useGame } from '../../../context/GameContext';

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default function ActivityPanel() {
  const { activities } = useGame();
  const totalDuration = activities.reduce((acc, a) => acc + a.duration, 0);

  return (
    <section className={styles.listSection}>
      <h2>Today's activities</h2>

      <div className={styles.row}>
        <div className={styles.activityTotals}>
          <span>{formatDuration(totalDuration)}</span>
          <span>time and</span>
          <span>{activities.length}</span>
          <span>activities logged today</span>
        </div>
      </div>

      {activities.length === 0 ? (
        <p>No activities completed today...so far!</p>
      ) : (
        <List
          items={activities}
          renderItem={(act) => (
            <>
              {act.name} – {formatDuration(act.duration)}
            </>
          )}
          className={styles.list}
        />
      )}
    </section>
  );
}
