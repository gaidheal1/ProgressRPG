import React, { useState, useEffect } from 'react';
import QuestModal from '../QuestModal/QuestModal';
import GameSection from '../GameSection';
import CurrentQuestDisplay from './CurrentQuestDisplay';
import QuestRewards from './QuestRewards';
import QuestStagesList from './QuestStagesList';
import { useGame } from '../../../context/GameContext';
import Button from '../../../components/Button/Button';
import ButtonFrame from '../../../components/Button/ButtonFrame';
import QuestTimer from '../../../components/Timer/QuestTimer';


export default function QuestSection() {
  const { questTimer } = useGame();
  const { status, assignSubject } = questTimer;
  const quest = questTimer.subject;
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (questTimer.isComplete && status === 'active') {
      completeQuest();
    }
  }, [questTimer.isComplete, status]);

  return (
    <GameSection type="Quest">
      <QuestTimer />
      <QuestStagesList stages={[]} />
      <QuestRewards rewards={{ xp: 0, coins: 0 }}/>
      <ButtonFrame>
        <Button
          className="primary"
          onClick={() => {
            console.log('Show quests button clicked');
            setModalOpen(true);
          }}
        >
          Show quests
        </Button>
      </ButtonFrame>
      {modalOpen && (
        <QuestModal
          onClose={() => setModalOpen(false)}
          onChooseQuest={(quest, duration) => {
            console.log('Quest selected:', quest.name, duration);
            assignSubject(quest, duration);
            setModalOpen(false);
          }}
        />
      )}
    </GameSection>
  );
}
