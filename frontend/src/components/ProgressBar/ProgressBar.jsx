import React, { useRef, useState, useEffect } from "react";
import styles from "./ProgressBar.module.scss";

const ProgressBar = ({
  value = 0,
  max = 100,
  label,
  color = "default",
  paused = false,
}) => {
  const percent = Math.min((value / max) * 100, 100);
  const fillRef = useRef(null);
  const [fillWidth, setFillWidth] = useState(0);
  const [labelWidth, setLabelWidth] = useState(0);

  // Measure fill and label widths to decide which label to show
  useEffect(() => {
    if (fillRef.current) {
      setFillWidth(fillRef.current.offsetWidth);
      // We'll measure label inside fill on next tick
      // or do it dynamically by refs if you want to be exact
    }
  }, [percent]);

  const showInsideLabel = fillWidth > labelWidth + 10;

  const progressClass = [
    styles.progressBarFill,
    styles[color] || styles.default,
    paused ? styles.paused : ""
  ].join(" ");

  return (
    <div className={styles.progressBarWrapper}>
      {label && !showInsideLabel && (
        <span className={styles.labelOutside}>{label}</span>
      )}
      <div className={styles.progressTrack}>
        <div
          ref={fillRef}
          className={[
            styles.progressBarFill,
            styles[color] || styles.default,
            paused ? styles.paused : "",
          ].join(" ")}
          style={{ width: `${percent}%` }}
        >
          {label && showInsideLabel && (
            <span className={styles.labelInside}>{label}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
