import { useNavigate } from 'react-router-dom';
import Button from '../../components/Button/Button';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <h1>🧙‍♂️ Welcome to Progress RPG</h1>
      <p>Embark on epic quests and master your time through focused activity.</p>
      <Button onClick={() => navigate('/game')}>
        Enter the game
      </Button>
    </div>
  );
}
