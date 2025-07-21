// GameContext.jsx
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { useBootstrapGameData } from '../hooks/useBootstrapGameData';
import { apiFetch } from '../../utils/api';
import useTimers from '../hooks/useTimers';

const GameContext = createContext();

const getFormattedDate = () => {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
  const dd = String(today.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export const useGame = () => {
  const context = useContext(GameContext);
  return context;
}

export const GameProvider = ({ children }) => {
  const { player, character, activityTimerInfo, questTimerInfo, loading, error } = useBootstrapGameData();
  const [activities, setActivities] = useState({ results: [], count: 0 });
  const [quests, setQuests] = useState([]);

  const activityTimer = useTimers({ mode: "activity" });
  const questTimer = useTimers({ mode: "quest" });
  console.log("acttimerinfo:", activityTimerInfo);

  useEffect(() => {
    if (activityTimerInfo || questTimerInfo) {
      activityTimer.loadFromServer(activityTimerInfo);
      questTimer.loadFromServer(questTimerInfo);
    }
  }, [activityTimerInfo, questTimerInfo]);


  console.log("acttimer:", activityTimer);

  const formattedDate = getFormattedDate();
  console.log("Formatted date:", formattedDate);
  async function fetchActivities() {
    const data = await apiFetch(`/activities/?date=${formattedDate}`);
    setActivities(data);
    console.log("fetchActivities response:", data);
  }
  useEffect(() => {
    fetchActivities();
  }, [formattedDate]);

  async function fetchQuests() {
    const data = await apiFetch(`/quests/eligible`);
    setQuests(data);
  }

  useEffect(() => {
    fetchQuests();
  }, [player, character]);

  const value = React.useMemo(() => ({
    player,
    character,
    activityTimer,
    questTimer,
    activities,
    fetchActivities,
    quests,
    fetchQuests,
  }), [player, character, activityTimer, questTimer, activities, fetchActivities, quests,fetchQuests]);


  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
};
