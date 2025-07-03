import React, { useState} from "react";
import { useGame } from "../../context/GameContext";
import Button from "../Button/Button";
import ButtonFrame from "../Button/ButtonFrame";
import Input from "../Input/Input";
import useCombinedTimers from "../../hooks/useCombinedTimers";
import { formatDuration } from "../../../utils/formatUtils.js";
import sharedStyles from "./Timer.module.scss";

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
  const displayTime = formatDuration(elapsedTime);

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

      <div className={sharedStyles.timerFrame>
        <div className={sharedStyles.timerText>{displayTime}</div>
      </div>
      <div className="timer-status">{status}</div>
      <ButtonFrame>
        <Button
          onClick={assignSubject}
          disabled={status !== "empty"}
        >
          Start Activity
        </Button>

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
