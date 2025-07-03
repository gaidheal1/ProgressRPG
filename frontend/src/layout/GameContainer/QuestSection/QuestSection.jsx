import React, { useState, useEffect } from 'react';
import QuestModal from '../QuestModal/QuestModal';
import GameSection from '../GameSection';
import CurrentQuestDisplay from './CurrentQuestDisplay';
import QuestRewards from './QuestRewards';
import QuestStagesList from './QuestStagesList';
import { useTimer } from '../../../context/TimerContext';
import Button from '../../../components/Button/Button';

export default function QuestSection() {
  const { questTimer } = useTimer();
  const quest = questTimer.subject;
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (questTimer.isComplete && questTimer.status === 'active') {
      onCompleteQuest();
    }
  }, [questTimer.isComplete, questTimer.status]);

  return (
    <GameSection type="Quest">
      <CurrentQuestDisplay quest={quest} />
      <QuestStagesList stages={[]} />
      <QuestRewards rewards={{ xp: 0, coins: 0 }}/>
      <div className="button-frame">
        <Button
          className="button-filled" id="show-quests-btn"
          onClick={() => setModalOpen(true)}
        >
          Show quests
        </Button>
      </div>
      {modalOpen && (
        <QuestModal
          onClose={() => setModalOpen(false)}
          onSelectQuest={(quest, duration) => {
            timer.assignSubject(quest, duration * 60);
            timer.start?.();
            setModalOpen(false);
          }}
        />
      )}
    </GameSection>
  );
}
