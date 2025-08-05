import React, { useEffect } from 'react';
import { BrowserRouter, useLocation } from 'react-router-dom';

import { GameProvider } from './context/GameContext';
import { useMaintenanceStatus } from './hooks/useMaintenanceStatus';
import { useAuth } from './context/AuthContext';

import AppRoutes from "./routes/AppRoutes";
import Navbar from './layout/Navbar/Navbar';
import Footer from './layout/Footer/Footer';
import FeedbackWidget from './components/FeedbackWidget/FeedbackWidget';
import StaticBanner from './components/StaticBanner/StaticBanner';
import MaintenancePage from "./pages/MaintenancePage";

import { initGA, logPageView } from '../utils/analytics';

import packageJson from '../package.json';
const appVersion = packageJson.version;
const announcement = `Progress RPG is in alpha status, and under active development. Bugs may appear, and data may be lost. Thank you for testing! Version ${appVersion}`;

function RouteChangeTracker() {
  const location = useLocation();

  useEffect(() => {
    logPageView(location.pathname + location.search);
  }, [location]);

  return null;
}


function App() {
  const { isAuthenticated } = useAuth();
  const maintenance = useMaintenanceStatus();

  useEffect(() => {
    initGA();
  }, [])


  if (maintenance.loading) {
    return <div>Loading...</div>
  }

  if (maintenance.active) {
    return <MaintenancePage {...maintenance.details} />;
  }

  return (
    <GameProvider>
      <BrowserRouter>
        <RouteChangeTracker />
        <div className="app-container">
          <Navbar />
          <StaticBanner message={announcement} />
          <AppRoutes />
          <Footer />
          {isAuthenticated && <FeedbackWidget />}
        </div>
      </BrowserRouter>
    </GameProvider>
  );
}

export default App;
