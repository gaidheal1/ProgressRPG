import { useEffect, useState } from 'react';
import { apiFetch } from '../../utils/api';
import useTimers from './useTimers';
import { useAuth } from '../context/AuthContext.jsx';

export function useBootstrapGameData() {
  const { isAuthenticated, loading: authLoading } = useAuth();

  const activityTimer = useTimers({ mode: "activity" });
  const questTimer = useTimers({ mode: "quest"});

  const [player, setPlayer] = useState(null);
  const [character, setCharacter] = useState(null);
  const [quests, setQuests] = useState([]);
  const [activities, setActivities] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !isAuthenticated) return;

    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const dd = String(today.getDate()).padStart(2, '0');
    const formattedDate = `${yyyy}-${mm}-${dd}`;

    const fetchGameData = async () => {
      try {
        setLoading(true);

        const [info, questsData, activitiesData] = await Promise.all([
          apiFetch('/fetch_info/'),
          apiFetch('/quests/eligible/'),
          apiFetch(`/activities/?date=${formattedDate}`)
        ]);
        setPlayer(info.profile);
        setCharacter(info.character);
        setQuests(questsData);
        setActivities(activitiesData);
        activityTimer.loadFromServer(info.activity_timer);
        questTimer.loadFromServer(info.quest_timer);

      } catch (err) {
        console.error('[Bootstrap] Error loading game data:', err);
        setError('Something went wrong while loading game data.');
      } finally {
        setLoading(false);
      }
    };

    fetchGameData();
  }, [authLoading, isAuthenticated]);

  return {
    player,
    character,
    activities,
    quests,
    activityTimer,
    questTimer,
    loading,
    error
  };
}
