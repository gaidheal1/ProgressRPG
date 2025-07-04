// hooks/useCombinedTimers.js
import { useEffect } from 'react';
import { useGame } from '../context/GameContext';

export default function useCombinedTimers() {
  const game = useGame();

  if (!game) {
    throw new Error("useCombinedTimers must be used within a GameProvider");
  }

  const { activityTimer, questTimer } = useGame();

  // Auto-pause activity when quest completes
  useEffect(() => {
    if (questTimer.status === "complete" && activityTimer.status === "active") {
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
    questTimer.status === "waiting";

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

  // Helper for external use
  const submitActivity = () => {
    console.log('[COMBINED TIMERS] Submit activity');
    activityTimer.complete();
    activityTimer.reset();
    questTimer.pause();
  };

  useEffect(() => {
    console.log('[COMBINED TIMERS] Complete quest');
    if (
      questTimer.status === "active" &&
      questTimer.remaining >= questTimer.duration
    ) {
      questTimer.complete();
      activityTimer.pause();
    }
  }, [questTimer.elapsed, questTimer.status]);

  return {
    submitActivity,
  };
}
