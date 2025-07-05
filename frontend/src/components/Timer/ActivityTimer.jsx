import React, { useState} from "react";
import { useGame } from "../../context/GameContext";
import Button from "../Button/Button";
import ButtonFrame from "../Button/ButtonFrame";
import Input from "../Input/Input";
import useCombinedTimers from "../../hooks/useCombinedTimers";
import { formatDuration } from "../../../utils/formatUtils.js";
import TimerDisplay from "./TimerDisplay.jsx";
import styles from "./ActivityTimer.module.scss";

export function ActivityTimer() {
  const [activityText, setActivityText] = useState('');
  const handleInputChange = (value) => {
    setActivityText(value); // record every change
  };

  const { activityTimer } = useGame();
  const {
    status,
    elapsed,
    assignSubject,
  } = activityTimer;
  const displayTime = formatDuration(elapsed);

  const { submitActivity } = useCombinedTimers();

  // console.log("Activity timer displayTime:", displayTime);

  return (
    <section className={styles.activityRow}>
      <TimerDisplay
        label="Activity"
        status={status}
        time={displayTime}
      />
      <Input
        id="activity-input"
        label="Activity"
        value={activityText}
        onChange={handleInputChange}
        placeholder="Enter activity"
      />
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
    </section>
  );
}
