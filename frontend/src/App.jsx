import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { GameProvider } from './context/GameContext';
import Navbar from './layout/Navbar/Navbar';

import Home from './pages/Home/Home';
import LoginPage from './pages/LoginPage/LoginPage';
import LogoutPage from './pages/LogoutPage/LogoutPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import Game from './pages/Game/Game';

import { useAuth } from './context/AuthContext';

import {
  HashRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

// import Profile from './pages/Profile'; // for future routes
// import NotFound from './pages/NotFound'; // optional 404


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
      <Navbar />
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
                <Game />
              </PrivateRoute>
            }
          />

          <Route path="*" element={<h2>404: Page Not Found</h2>} />
        </Routes>
      </main>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <GameProvider>
        <HashRouter>
          <div className="app-container">
            <AppRoutes />
            <footer style={{ marginTop: '2rem', textAlign: 'center' }}>
              <small>&copy; 2025 Progress RPG</small>
            </footer>
          </div>
        </HashRouter>
      </GameProvider>
    </AuthProvider>
  );
}

export default App;
