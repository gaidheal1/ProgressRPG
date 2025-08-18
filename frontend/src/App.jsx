import React, { useEffect } from 'react';
import { BrowserRouter, useLocation } from 'react-router-dom';

import { MaintenanceProvider } from './context/MaintenanceContext';
import { ToastProvider } from './context/ToastContext';
import { GameProvider } from './context/GameContext';
import { WebSocketProvider } from './context/WebSocketContext';

import { useAuth } from './context/AuthContext';

import AppRoutes from "./routes/AppRoutes";
import Navbar from './layout/Navbar/Navbar';
import Footer from './layout/Footer/Footer';
import FeedbackWidget from './components/FeedbackWidget/FeedbackWidget';
import StaticBanner from './components/StaticBanner/StaticBanner';

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

  useEffect(() => {
    initGA();
  }, [])


  return (
    <MaintenanceProvider>
      <ToastProvider>
        <GameProvider>
          <WebSocketProvider>
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
          </WebSocketProvider>
        </GameProvider>
      </ToastProvider>
    </MaintenanceProvider>
  );
}

export default App;
