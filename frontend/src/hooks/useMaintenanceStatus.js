import { useState, useEffect } from 'react';
import { apiFetch } from '../../utils/api';

export function useMaintenanceStatus() {
  const [maintenance, setMaintenance] = useState({
    loading: true,
    active: false,
    details: null,
  });

  useEffect(() => {
    async function fetchMaintenance() {
      try {
        const data = await apiFetch('/maintenance-status/');

        if (data.maintenance_active) {
          setMaintenance({
            loading: false,
            active: true,
            details: {
              name: data.name,
              description: data.description,
              startTime: data.start_time,
              endTime: data.end_time,
            },
          });
        } else {
          setMaintenance({ loading: false, active: false, details: null });
        }
      } catch (error) {
        console.error('Error fetching maintenance status:', error);
        setMaintenance({ loading: false, active: false, details: null });
      }
    }

    fetchMaintenance();
  }, []);

  return maintenance;
}
