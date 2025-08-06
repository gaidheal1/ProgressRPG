// hooks/useToasts.js
import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

export function useToasts(duration = 3300) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message) => {
    const id = uuidv4();
    setToasts((prev) => [...prev, { id, message: String(message) }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, duration);
  }, [duration]);

  return { toasts, showToast };
}
