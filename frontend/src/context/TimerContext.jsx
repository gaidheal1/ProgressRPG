import React, { createContext, useContext, useEffect } from "react";
import useTimers from "../hooks/useTimers";

const TimerContext = createContext();

export const useTimer = () => useContext(TimerContext);

export const TimerProvider = ({ children }) => {
  const activityTimer = useTimers({ mode: "activity" });
  const questTimer = useTimers({ mode: "quest", initialDuration: 600 });

  // Cross-timer logic: when quest completes, pause activity
  useEffect(() => {
    if (questTimer.status === "completed" && activityTimer.status === "active") {
      activityTimer.pause();
    }
  }, [questTimer.status]);

  // Cross-timer logic: when quest time runs out (completed), you can add toast or other side effects here

  // Function to start both if both ready
  const startBothIfReady = () => {
    const bothReady =
      activityTimer.status === "waiting" &&
      questTimer.status === "waiting" &&
      activityTimer.elapsed === 0 &&
      questTimer.elapsed === 0;
    if (bothReady) {
      activityTimer.start();
      questTimer.start();
    }
  };

  // Call startBothIfReady when statuses change or externally (could add dependencies to useEffect)
  useEffect(() => {
    startBothIfReady();
  }, [activityTimer.status, questTimer.status]);

  // Submit activity: complete activity and pause quest if active
  const submitActivity = () => {
    activityTimer.reset(); // or complete(), depending on your flow
    if (questTimer.status === "active") {
      questTimer.pause();
    }
  };

  // Complete quest: complete quest and pause activity if active
  const completeQuestAndPauseActivity = () => {
    // Assuming your hook doesn't have complete(), you might implement it as reset + status change
    questTimer.reset();
    if (activityTimer.status === "active") {
      activityTimer.pause();
    }
  };

  return (
    <TimerContext.Provider
      value={{
        activityTimer,
        questTimer,
        submitActivity,
        completeQuestAndPauseActivity,
        startBothIfReady,
      }}
    >
      {children}
    </TimerContext.Provider>
  );
};
