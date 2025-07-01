import { useState, useEffect } from 'react';

export function useActivities() {
  const [activities, setActivities] = useState([]);
  const [error, setError] = useState(null);

  const fetchActivities = async () => {
    try {
      const response = await fetch('/fetch_activities/', { method: 'GET' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      if (data.success) {
        setActivities(data.activities);
      } else {
        setError('API returned failure');
      }
    } catch (err) {
      setError(err.message || 'Unknown error');
    }
  };

  useEffect(() => {
    fetchActivities(); // auto-load on mount
  }, []);

  return { activities, setActivities, error };
}
