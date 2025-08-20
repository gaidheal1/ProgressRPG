// components/Toast/ToastManager.jsx

import styles from './Toast.module.scss';

export default function ToastManager({ messages }) {
  return (
    <div className={styles.toastContainer} role="alert" aria-live="assertive">
      {messages.map(({ id, message }) => (
        <div key={id} className={styles.toast}>
          {message}
        </div>
      ))}
    </div>
  );
}
