import React from "react";
import styles from "./ProgressBar.module.scss";

const ProgressBar = ({
  value = 0,
  max = 100,
  label,
  color = "default",
  paused = false,
}) => {
  const percent = Math.min((value / max) * 100, 100);

  const progressClass = [
    styles.progressBarFill,
    styles[color] || styles.default,
    paused ? styles.paused : ""
  ].join(" ");

  return (
    <div className={styles.progressBarWrapper}>
      {label && <span className={styles.label}>{label}</span>}
      <div className={styles.progressTrack}>
        <div
          className={progressClass}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
