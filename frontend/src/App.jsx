import React from 'react';
import { GameProvider } from './context/GameContext';
import { ErrorBoundary } from 'react-error-boundary';
import { useMaintenanceStatus } from './hooks/useMaintenanceStatus';
import ErrorFallback from './components/ErrorFallback';
import Navbar from './layout/Navbar/Navbar';
import Footer from './layout/Footer/Footer';
import FeedbackWidget from './components/FeedbackWidget/FeedbackWidget';
import StaticBanner from './components/StaticBanner/StaticBanner';

import Home from './pages/Home/Home';
import LoginPage from './pages/LoginPage/LoginPage';
import LogoutPage from './pages/LogoutPage/LogoutPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import OnboardingPage from './pages/OnboardingPage/OnboardingPage';
import Game from './pages/Game/Game';
import ProfilePage from './pages/Profile/Profile';
import ConfirmationPage from './pages/ConfirmationPage';
import MaintenancePage from './pages/MaintenancePage';
// import NotFound from './pages/NotFound'; // optional 404

import packageJson from '../package.json';
import { useAuth } from './context/AuthContext';

import {
  HashRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

import PrivateRoute from './components/PrivateRoute';
import RequireOnboardingComplete from './components/RequireOnboardingComplete';

const appVersion = packageJson.version;


function AppRoutes() {
  return (
    <>
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/logout" element={<LogoutPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/confirm_email/:key" element={<ConfirmationPage />} />

            {/* Protected routes */}
            <Route
              path="/onboarding"
              element={
                <PrivateRoute>
                  <OnboardingPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/game"
              element={
                <PrivateRoute>
                  <RequireOnboardingComplete>
                    <ErrorBoundary FallbackComponent={ErrorFallback}>
                      <Game />
                    </ErrorBoundary>
                  </RequireOnboardingComplete>
                </PrivateRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <PrivateRoute>
                  <ErrorBoundary FallbackComponent={ErrorFallback}>
                    <ProfilePage />
                  </ErrorBoundary>
                </PrivateRoute>
              }
            />
            <Route path="*" element={<h2>404: Page Not Found</h2>} />
          </Routes>
        </main>
      </ErrorBoundary>
    </>
  );
}

function App() {
  const { isAuthenticated } = useAuth();
  const announcement = `Progress RPG is in alpha status, and under active development. Bugs may appear, and data disappear, without warning. Version ${appVersion}`;
  const maintenance = useMaintenanceStatus();

  if (maintenance.loading) {
    return <div>Loading...</div>
  }

  if (maintenance.active) {
    return <MaintenancePage {...maintenance.details} />;
  }
  return (
    <GameProvider>
      <HashRouter>
        <div className="app-container">
          <Navbar />
          <StaticBanner message={announcement} />
          <AppRoutes />
          <Footer />
          {isAuthenticated && <FeedbackWidget />}
        </div>
      </HashRouter>
    </GameProvider>
  );
}

export default App;
