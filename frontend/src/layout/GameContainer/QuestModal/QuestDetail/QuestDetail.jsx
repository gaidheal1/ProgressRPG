import React from 'react';
import Button from '../../../../components/Button/Button';
import styles from './QuestDetail.module.scss';

export default function QuestDetail({ quest, selectedDuration, onDurationChange, onChoose }) {
  if (!quest) {
    return <p className={styles.placeholder}>Please select a quest from the list</p>;
  }

  //console.log('[QUEST DETAIL] Quest:', quest);

  return (
    <section className={styles.questDetail}>
      <h3>{quest.name}</h3>
      <p>{quest.description}</p>

      {quest.duration_choices && quest.duration_choices.length > 0 && (
        <div className={styles.durationSelector}>
          <label htmlFor="duration-select">Select duration:</label>
          <select
            id="duration-select"
            value={selectedDuration}
            onChange={(e) => onDurationChange(Number(e.target.value))}
          >
            {quest.duration_choices.map((duration) => {
              const mins = Math.floor(duration / 60);
              const secs = duration % 60;
              const display = `${mins ? ` ${mins} min${mins !== 1 ? 's' : ''}` : ''}${secs ? ` ${secs} sec${secs !== 1 ? 's' : ''}` : ''}`;

              return (
                <option key={duration} value={duration}>
                  {display}
                </option>
              );
            })}
          </select>
        </div>
      )}

      <Button
        className="primary"
        onClick={onChoose}
        disabled={!selectedDuration}
      >
        Select Quest
      </Button>
    </section>
  );
}
