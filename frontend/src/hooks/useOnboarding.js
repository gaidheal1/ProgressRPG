// src/hooks/useOnboarding.js
import { useState } from 'react';
import { apiFetch } from '../../utils/api';

export default function useOnboarding() {
  const [step, setStep] = useState(null);
  const [error, setError] = useState('');

  const progress = async (payload = {}) => {
    try {
      const data = await apiFetch('/onboarding/progress/', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setStep(data.step);
      return data;
    } catch (err) {
      console.error('[Onboarding] Error:', err);
      setError(err.message || 'Failed to progress onboarding');
      return null;
    }
  };

  return { step, progress, error };
}
