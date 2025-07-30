import React from "react";
import styles from "./StaticBanner.module.scss";


const StaticBanner = ({ message }) => {
  if (!message) return null;
  return (
    <div className={styles.banner}>
      <p className={styles.bannerText}>{message}</p>
    </div>
  );
};

export default StaticBanner;
