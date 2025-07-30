import React, { useState } from "react";
import styles from "./FeedbackWidget.module.scss";
import Button from "../Button/Button";

const FeedbackWidget = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleModal = () => setIsOpen(!isOpen);

  return (
    <div className={styles.feedbackWidget}>
      <Button className={styles.feedbackButton} onClick={toggleModal}>
        💬 Feedback
      </Button>

      {isOpen && (
        <div className={styles.feedbackModal}>
          <div className={styles.modalContent}>
            <Button className={styles.closeButton} onClick={toggleModal}>
              ×
            </Button>
            <h3>Help us improve Progress RPG</h3>
            <p>Spotted a bug? Got an idea? Choose where to send your feedback:</p>
            <div className={styles.buttonGroup}>
              <a
                href="https://github.com/gaidheal1/ProgressRPG/issues/new/choose"
                target="_blank"
                rel="noopener noreferrer"
                className={`${styles.modalButton} ${styles.github}`}
              >
                👩‍💻 GitHub
              </a>
              <a
                href="https://forms.gle/7MnVUirk25GWhVfy9"
                target="_blank"
                rel="noopener noreferrer"
                className={`${styles.modalButton} ${styles.form}`}
              >
                💡 Google Form
              </a>
              <a
                href="https://discord.gg/6AEd2zhY"
                target="_blank"
                rel="noopener noreferrer"
                className={`${styles.modalButton} ${styles.discord}`}
              >
                👥 Join Discord
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackWidget;
