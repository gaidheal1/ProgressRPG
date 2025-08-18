import React, { useEffect } from 'react';
import styles from './MaintenancePage.module.scss';
import { useMaintenanceStatus } from '../../hooks/useMaintenanceStatus';

export default function MaintenancePage() {
  const { active, details, refetch } = useMaintenanceStatus();

  // Optional: fetch maintenance when component mounts
  useEffect(() => {
    refetch();
  }, [refetch]);

  if (!active || !details) {
    return <p>No maintenance scheduled.</p>;
  }

  return (
    <div className={styles.MaintenancePage}>
      <h1>Site Under Maintenance</h1>
      <p>{details.name}</p>
      <p>{details.description}</p>
      <p>
        Scheduled from: {new Date(details.startTime).toLocaleString()} <br />
        Until: {new Date(details.endTime).toLocaleString()}
      </p>
      <p>We apologise for the inconvenience. Please check back later.</p>
    </div>
  );
}
