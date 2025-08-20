// context/MaintenanceContext.js
import React, { createContext, useContext, useState } from 'react';

const MaintenanceContext = createContext();

export function MaintenanceProvider({ children }) {
  const [maintenance, setMaintenance] = useState({
    active: false,
    details: null,
    previousLocation: null,
    justEnded: false,
  });

  return (
    <MaintenanceContext.Provider value={{ maintenance, setMaintenance }}>
      {children}
    </MaintenanceContext.Provider>
  );
}

export function useMaintenanceContext() {
  const context = useContext(MaintenanceContext);
  if (!context) {
    throw new Error('useMaintenanceContext must be used within a MaintenanceProvider');
  }
  return context;
}
