// QuestDetails.jsx
import styles from './QuestDetail.module.scss';
import Button from '../../../../components/Button/Button';

export default function QuestDetails({ selectedQuest, selectedDuration, setSelectedDuration, handleSelect }) {
  return (
    <div >
      {selectedQuest ? (
        <QuestPanel
          quest={selectedQuest}
          onDurationChange={setSelectedDuration}
        />
      ) : (
        <p>Select a quest to see details</p>
      )}

      <div class="button-frame" >
        <Button
          onClick={handleSelect}
          disabled={!selectedQuest || !selectedDuration}
        >
          Start Quest
        </Button>
      </div>
    </div>
  );
}
