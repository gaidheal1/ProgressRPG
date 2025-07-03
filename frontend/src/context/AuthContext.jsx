import { createContext, useContext, useState, useEffect } from 'react';
import { apiFetch } from '../../utils/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('refreshToken'));
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Use the centralized apiFetch here
  const authFetch = async (path, options = {}) => {
    return apiFetch(path, options);
  };

  useEffect(() => {
    async function verifyUser() {
      const token = localStorage.getItem('accessToken');
      const refresh = localStorage.getItem('refreshToken');

      if (!token || !refresh) {
        setLoading(false);
        setIsAuthenticated(false);
        return;
      }

      try {
        // Use apiFetch here to auto handle token refresh etc.
        const userData = await apiFetch('/me/');
        setUser(userData);
        setAccessToken(token);
        setRefreshToken(refresh);
        setIsAuthenticated(true);
      } catch (err) {
        logout();
      } finally {
        setLoading(false);
      }
    }

    verifyUser();
  }, []);

  const login = (access, refresh) => {
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    setAccessToken(access);
    setRefreshToken(refresh);
    setIsAuthenticated(true);

    // Fetch user info after login
    apiFetch('/me/')
      .then(setUser)
      .catch(() => setUser(null));
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    accessToken,
    refreshToken,
    isAuthenticated,
    user,
    setUser,
    login,
    logout,
    authFetch,
    loading,
  };

  return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
