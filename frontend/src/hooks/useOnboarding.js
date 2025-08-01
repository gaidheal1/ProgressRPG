// src/hooks/useOnboarding.js
import { useEffect, useState } from 'react';
import { apiFetch } from '../../utils/api';

export default function useOnboarding() {
  console.log('useOnboarding render');
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Load current onboarding step on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await apiFetch('/onboarding/status/');
        console.log("useOnboarding api data:", data);
        setStep(data.step);
        setError('');
      } catch (err) {
        console.error('[Onboarding] Status error:', err);
        setError('Failed to fetch onboarding status.');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);


  const progress = async (payload = {}) => {
    try {
      const data = await apiFetch('/onboarding/progress/', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      console.log("useOnboarding api data:", data);
      if (typeof data.step === 'number') {
        setStep(data.step);
      }
      setError('');
      return data;
    } catch (err) {
      console.error('[Onboarding] Progress error:', err);
      setError(err.message || 'Failed to progress onboarding');
      return null;
    }
  };

  return { step, progress, error, loading };
}
