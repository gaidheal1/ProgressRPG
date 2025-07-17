import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { GameProvider } from './context/GameContext';
import { ErrorBoundary } from 'react-error-boundary';
import ErrorFallback from './components/ErrorFallback';
import Navbar from './layout/Navbar/Navbar';
import Footer from './layout/Footer/Footer';
import FeedbackWidget from './components/FeedbackWidget/FeedbackWidget';

import Home from './pages/Home/Home';
import LoginPage from './pages/LoginPage/LoginPage';
import LogoutPage from './pages/LogoutPage/LogoutPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import Game from './pages/Game/Game';
import ProfilePage from './pages/Profile/Profile';
// import NotFound from './pages/NotFound'; // optional 404

import { useAuth } from './context/AuthContext';

import {
  HashRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';


function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>; // or spinner
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

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
		            <ErrorBoundary FallbackComponent={ErrorFallback}>
                  <Game />
		            </ErrorBoundary>
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

  return (
    <AuthProvider>
      <GameProvider>
        <HashRouter>
          <div className="app-container">
            <Navbar />
            <AppRoutes />
            <Footer />
            {isAuthenticated && <FeedbackWidget />}
          </div>
        </HashRouter>
      </GameProvider>
    </AuthProvider>
  );
}

export default App;
