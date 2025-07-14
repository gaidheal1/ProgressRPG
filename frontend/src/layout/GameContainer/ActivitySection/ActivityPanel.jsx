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
      <p className={styles.listSectionHeader}>Today's activities</p>

      <div className={styles.activityTotals}>
        <span id="activities-time-message">Total time:</span>
        <span id="activities-time-data">{formatDuration(totalDuration)}</span>
        <span id="activities-total-message">Activities logged:</span>
        <span id="activities-total-data">{activities.length}</span>
      </div>

      {activities.length === 0 ? (
        <p>Searching for activities completed today...</p>
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
