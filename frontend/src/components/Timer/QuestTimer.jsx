import React from "react";
import { useGame } from "../../context/GameContext";
import Button from "../Button/Button";
import { useCombinedTimers } from "../../hooks/useCombinedTimers.js";

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function QuestTimer() {
  const { questTimer } = useGame();
  const {
    status,
    elapsedTime,
    remainingTime,
    duration,
  } = questTimer;

  const { completeQuest } = useCombinedTimers();

  return (
    <div className="timer quest-timer">
      <div className="timer-display">{formatTime(remainingTime)}</div>
      <div className="timer-status">{status}</div>
    </div>
  );
}
