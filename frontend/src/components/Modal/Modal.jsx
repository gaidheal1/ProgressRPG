import React from "react";
import styles from "./Modal.module.scss";
import Button from "../Button/Button"

export default function Modal({ title, children, onClose }) {
  return (
    <div className={styles.modalBackdrop}>
      <div className={styles.modal}>
        <header className={styles.modalHeader}>
          <h2>{title}</h2>
          <Button
            onClick={onClose}
            aria-label="Close modal"
            className={styles.closeButton}
          >
            &times;
          </Button>
        </header>
        <div className={styles.modalContent}>
          {children}
        </div>
      </div>
    </div>
  );
}
