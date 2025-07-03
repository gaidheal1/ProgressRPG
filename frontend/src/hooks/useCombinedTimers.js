// hooks/useCombinedTimers.js
import { useEffect } from 'react';
import { useGame } from '../context/GameContext';

export default function useCombinedTimers(activityTimer, questTimer) {
  // const { activityTimer, questTimer } = useGame();

  // Auto-pause activity when quest completes
  useEffect(() => {
    if (questTimer.status === "completed" && activityTimer.status === "active") {
      activityTimer.pause();
    }
  }, [
    questTimer.status,
    activityTimer.status
  ]);

  // Auto-start both if both are ready
  useEffect(() => {
    console.log('[COMBINED TIMERS] effect check (both ready)');
    const bothReady =
    activityTimer.status === "waiting" &&
    questTimer.status === "waiting" &&
    activityTimer.elapsed === 0 &&
    questTimer.elapsed === 0;

    if (bothReady) {
      console.log('[COMBINED TIMERS] Both ready!');
      activityTimer.start();
      questTimer.start();
    }
  }, [
    activityTimer.status,
    questTimer.status,
    activityTimer.elapsed,
    questTimer.elapsed
  ]);

  // Helpers for external use
  const submitActivity = () => {
    console.log('[COMBINED TIMERS] Submit activity');
    activityTimer.complete();
    activityTimer.reset();
    if (questTimer.status === "active") {
        questTimer.pause();
    }
};

const completeQuest = () => {
    console.log('[COMBINED TIMERS] Complete quest');
    questTimer.complete();
    if (activityTimer.status === "active") {
      activityTimer.pause();
    }
  };

  return {
    submitActivity,
    completeQuest,
  };
}
