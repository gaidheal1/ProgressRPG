import React from 'react';
import List from '../../../components/List/List';
import styles from './QuestStagesList.module.scss';

export default function QuestStagesList({ stages = [] }) {
  return (
    <div className={`${styles.container} section-row`}>
      <p className={styles.title}><strong>Quest stages</strong></p>

      <div className={styles.listWrapper}>
        {stages.length === 0 ? (
          <p className={styles.noProgress}>No quest progress yet.</p>
        ) : (
          <List
            items={stages}
            renderItem={(stage) => stage}
            className={styles.list}
            sectionClass={styles.listSection}
          />
        )}
      </div>
    </div>
  );
}
