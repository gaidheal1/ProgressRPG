import React from 'react';
import styles from './ButtonFrame.module.scss';

export default function ButtonFrame({ children }) {
  return <div className={styles.buttonFrame}>{children}</div>;
}
