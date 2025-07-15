import React, { useState } from 'react';
import QuestList from './QuestList/QuestList.jsx';
import QuestDetail from './QuestDetail/QuestDetail.jsx';
import styles from './QuestModal.module.scss';
import { useGame } from '../../../context/GameContext.jsx';
import Button from '../../../components/Button/Button.jsx';

export default function QuestModal({ onClose, onChooseQuest }) {
  const { quests } = useGame();
  const [selectedQuest, setSelectedQuest] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState(null);

  const handleViewQuest = (quest) => {
    setSelectedQuest(quest);
    setSelectedDuration(quest.duration_choices?.[0] || null);
  };

  const handleChooseQuest = () => {
    console.log('onChoose!')
    if (!selectedQuest || !selectedDuration) return;

    console.log('Still here!')
    onChooseQuest?.(selectedQuest, selectedDuration);
    console.log('Selected, duration:', selectedQuest, selectedDuration);

    onClose();
  };

  return (
    <div className={styles.modalBackdrop}>
      <div className={styles.modal}>

        <header className={styles.modalHeader}>
          <h2>Choose your quest</h2>
          <Button
            onClick={onClose}
            aria-label="Close modal"
            className={styles.closeButton}
          >
            &times;
          </Button>
        </header>
        <div className={styles.modalContent}>
          <QuestList
            quests={quests}
            selectedQuest={selectedQuest}
            onSelect={handleViewQuest}
          />
          <QuestDetail
            quest={selectedQuest}
            selectedDuration={selectedDuration}
            onDurationChange={setSelectedDuration}
            onChoose={handleChooseQuest}
          />
        </div>
      </div>
    </div>
  );
}
