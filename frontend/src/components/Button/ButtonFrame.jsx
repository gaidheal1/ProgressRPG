import React from 'react';
import styles from './ButtonFrame.module.scss'; // or .css if you prefer

export default function ButtonFrame({ children }) {
  return <div className={styles.buttonFrame}>{children}</div>;
}
