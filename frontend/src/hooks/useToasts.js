// useToasts.js
import { useState, useCallback } from 'react';

export function useToasts(duration = 3300) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message) => {
    setToasts((prev) => [...prev, String(message)]);
    setTimeout(() => {
      setToasts((prev) => prev.slice(1));
    }, duration);
  }, [duration]);

  return { toasts, showToast };
}
