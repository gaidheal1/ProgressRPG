// QuestList.jsx
import styles from './QuestList.module.scss';
import Button from '../../../../components/Button/Button';

export default function QuestList({ quests, selectedQuest, setSelectedQuest, setSelectedDuration }) {
  return (
    <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
      {quests.map((q, i) => (
        <li key={i}>
          <Button
            onClick={() => {
              setSelectedQuest(q);
              setSelectedDuration(q.duration_options?.[0] ?? 60);
            }}

          >
            {q.name}
          </Button>
        </li>
      ))}
    </ul>
  );
}
