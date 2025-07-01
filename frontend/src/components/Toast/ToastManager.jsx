import { useEffect, useState } from 'react';
import styles from './Toast.module.scss';

export default function ToastManager({ messages }) {
  const [visibleMessages, setVisibleMessages] = useState([]);

  useEffect(() => {
    const newToasts = messages.map((msg, index) => {
      const id = typeof msg === 'object' && msg.id ? msg.id : `${Date.now()}-${index}`;
      return { id, content: normalizeMessage(msg) };
    });

    setVisibleMessages(newToasts);

    const timer = setTimeout(() => {
      setVisibleMessages([]);
    }, 3500); // 0.3s in + 3s hold + 0.2s out

    return () => clearTimeout(timer);
  }, [messages]);

  function normalizeMessage(msg) {
    if (typeof msg === 'string') return msg;
    if (typeof msg === 'object' && msg.message) return msg.message;
    return JSON.stringify(msg);
  }

  return (
    <div className={styles.toastContainer} role="alert" aria-live="assertive">
      {visibleMessages.map(({ id, content }) => (
        <div key={id} className={styles.toast}>
          {content}
        </div>
      ))}
    </div>
  );
}
