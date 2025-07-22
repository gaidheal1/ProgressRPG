// hooks/useCombinedTimers.js
import { useRef, useEffect } from 'react';
import { useGame } from '../context/GameContext';

export default function useCombinedTimers() {
  const { activityTimer, questTimer, fetchActivities, fetchQuests } = useGame();
  const timersRunningRef = useRef(false);

  // Auto-start both if both are ready
  useEffect(() => {
    const isReady = (status) => ["waiting", "paused"].includes(status);
    const bothReady = isReady(activityTimer.status) && isReady(questTimer.status);

    if (bothReady && !timersRunningRef.current) {
      console.log('[COMBINED TIMERS] Both ready!');
      timersRunningRef.current = true;

      (async () => {
        if (activityTimer.status === "waiting" || activityTimer.status === "paused") {
          await activityTimer.start();
        }
        if (questTimer.status === "waiting" || questTimer.status === "paused") {
          await questTimer.start();
        }
      })();
    }
  }, [
    activityTimer.status,
    questTimer.status,
  ]);

  // Submit activity
  const submitActivity = async () => {
    console.log('[COMBINED TIMERS] Submit activity');

    timersRunningRef.current = false;

    await activityTimer.complete();
    await activityTimer.reset();
    await fetchActivities();
    if (questTimer.status !== "complete") questTimer.pause();
  };

  // Quest auto-complete
  useEffect(() => {
    console.log('[COMBINED TIMERS] Complete quest');

    if (
      questTimer.status === "active" &&
      questTimer.remaining <= 0
    ) {
      questTimer.complete();
      fetchQuests();
      activityTimer.pause();
      timersRunningRef.current = false;
    }
  }, [questTimer.elapsed, questTimer.status]);

  return {
    submitActivity,
  };
}
