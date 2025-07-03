import React, { useState} from "react";
import { useGame } from "../../context/GameContext";
import Button from "../Button/Button";
import ButtonFrame from "../Button/ButtonFrame";
import Input from "../Input/Input";
import useCombinedTimers from "../../hooks/useCombinedTimers";

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function ActivityTimer() {
  const [activityText, setActivityText] = useState('');
  const handleInputChange = (value) => {
    setActivityText(value); // record every change
  };

  const { activityTimer, questTimer } = useGame();
  const {
    status,
    elapsedTime,
    assignSubject,
  } = activityTimer;
  const { submitActivity } = useCombinedTimers(activityTimer, questTimer);
  return (
    <div className="timer activity-timer">
      <Input
        id="activity-input"
        label="Activity"
        value={activityText}
        onChange={handleInputChange}
        placeholder="Enter activity"
      />

      <div className="timer-display">{formatTime(elapsedTime)}</div>
      <div className="timer-status">{status}</div>
      <ButtonFrame>
        <Button
          onClick={assignSubject}
          disabled={status !== "empty"}
        >
          Start Activity
        </Button>

        {/* <Button onClick={pause} disabled={status !== "active"}>
          Pause
        </Button> */}

        {/* If you want to submit or complete the activity */}
        <Button
          onClick={() => {
            /* submit or complete handler */
            console.log("Submit activity:", activityText);
            setActivityText('');
            submitActivity();
          }}
          disabled={status === "empty"}
          >
          Submit Activity
        </Button>
      </ButtonFrame>
    </div>
  );
}
