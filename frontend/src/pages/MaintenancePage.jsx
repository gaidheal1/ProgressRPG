import React from 'react';

export default function MaintenancePage({ name, description, startTime, endTime }) {
  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center',
      padding: '2rem',
      backgroundColor: '#f5f5f5',
      color: '#333',
      fontFamily: 'sans-serif',
    }}>
      <h1>Site Under Maintenance</h1>
      <p>{name}</p>
      <p>{description}</p>
      <p>
        Scheduled from: {new Date(startTime).toLocaleString()} <br />
        Until: {new Date(endTime).toLocaleString()}
      </p>
      <p>We apologise for the inconvenience. Please check back later.</p>
    </div>
  );
}
