import React from 'react';
import styles from './QuestList.module.scss';
import Button from '../../../../components/Button/Button';

export default function QuestList({ quests, selectedQuest, onSelect }) {
  return (
    <nav className={styles.questList}>
      <ul>
        {quests?.map((quest) => (
          <li key={quest.id ?? quest.name}>
            <Button
              className={selectedQuest?.id === quest.id ? styles.selected : ''}
              onClick={() => onSelect(quest)}
            >
              {quest.name}
            </Button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
