import React from "react";
import { useTimer } from "../../context/TimerContext";
import Button from "../Button/Button";

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function QuestTimer({ onComplete, onPause, onReset }) {
  const { questTimer } = useTimer();
  const {
    status,
    elapsedTime,
    duration,
    start,
    pause,
    reset,
    setStatus,
  } = questTimer;

  const remainingTime = Math.max(duration - elapsedTime, 0);

  // Auto-complete logic moved here to keep in sync with context state
  React.useEffect(() => {
    if (remainingTime === 0 && status === "active") {
      pause();
      setStatus("completed");
      if (onComplete) onComplete();
    }
  }, [remainingTime, status, pause, setStatus, onComplete]);

  return (
    <div className="timer quest-timer">
      <div className="timer-display">{formatTime(remainingTime)}</div>
      <div className="timer-status">{status}</div>

      <Button onClick={start} disabled={status === "active"}>
        Start
      </Button>
      <Button onClick={() => { pause(); if (onPause) onPause(); }} disabled={status !== "active"}>
        Pause
      </Button>
      <Button onClick={() => { reset(); if (onReset) onReset(); }}>
        Reset
      </Button>
    </div>
  );
}
