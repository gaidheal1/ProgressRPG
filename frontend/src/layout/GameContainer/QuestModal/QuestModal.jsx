import React, { useState } from 'react';
import QuestPanel from './QuestPanel'; // your existing quest detail component
import QuestList from './QuestList/QuestList.jsx';
import QuestDetail from './QuestDetail/QuestDetail.jsx';
import styles from './QuestModal.module.scss';
import { useGame } from '../../../context/GameContext.jsx';

export default function QuestModal({ onClose, onSelectQuest }) {
  const quests = useGame();
  const [selectedQuest, setSelectedQuest] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState(null);

  const handleSelect = () => {
    if (!selectedQuest || !selectedDuration) return;

      onSelectQuest?.(selectedQuest, selectedDuration);
      onClose(); // Close modal after submission

  };

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <h3>Available Quests</h3>
        <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
          {quests.map((q, i) => (
            <li key={i}>
              <button
                onClick={() => {
                  setSelectedQuest(q);
                  setSelectedDuration(q.duration_options?.[0] ?? 60);
                }}
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'left',
                  margin: '0.25rem 0',
                  background: selectedQuest?.name === q.name ? '#e2e8f0' : 'transparent'
                }}
              >
                {q.name}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ flex: 2 }}>
        {selectedQuest ? (
          <QuestPanel
            quest={selectedQuest}
            onDurationChange={setSelectedDuration}
          />
        ) : (
          <p>Select a quest to see details</p>
        )}

        <div style={{ marginTop: '1rem' }}>
          <button
            onClick={handleSelect}
            disabled={!selectedQuest || !selectedDuration}
          >
            Start Quest
          </button>
        </div>
      </div>
    </div>
  );
}
