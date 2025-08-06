import { useEffect, useState } from 'react';
import { apiFetch } from '../../utils/api';
import { useAuth } from '../context/AuthContext.jsx';

export function useBootstrapGameData() {
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [player, setPlayer] = useState(null);
  const [character, setCharacter] = useState(null);
  const [activityTimerInfo, setActivityTimerInfo] = useState(null);
  const [questTimerInfo, setQuestTimerInfo] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !isAuthenticated) return;


    const fetchGameData = async () => {
      try {
        setLoading(true);

        const info = await apiFetch('/fetch_info/');
        setPlayer(info.profile);
        setCharacter(info.character);
        //console.log("info:", info);
        setActivityTimerInfo(info.activity_timer);
        setQuestTimerInfo(info.quest_timer);
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
    activityTimerInfo,
    questTimerInfo,
    loading,
    error
  };
}
