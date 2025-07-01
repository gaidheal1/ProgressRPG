import React, { useState, useEffect } from 'react';
import Game from './pages/Game/Game';
import Home from './pages/Home/Home';
import LoginPage from './pages/LoginPage/LoginPage';
import LogoutPage from './pages/LogoutPage/LogoutPage';
import Navbar from './layout/Navbar/Navbar';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import {
  HashRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';
import OnboardingPage from './pages/OnboardingPage';
import { GameProvider } from './context/GameContext';

// import Profile from './pages/Profile'; // for future routes
// import NotFound from './pages/NotFound'; // optional 404

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <AuthProvider>
      <GameProvider>
        <HashRouter>
          <div className="app-container">
            <header>
              <Navbar />
            </header>
            <main>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/logout" element={<LogoutPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/onboarding" element={
                  isAuthenticated ? <OnboardingPage /> : <Navigate to="/login" replace />
                } />
                <Route path="/game" element={
                  isAuthenticated ? <Game /> : <Navigate to="/login" replace />
                } />
                <Route path="*" element={<h2>404: Page Not Found</h2>} />
              </Routes>
            </main>
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
