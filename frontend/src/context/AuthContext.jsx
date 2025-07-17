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
      if (!accessToken || !refreshToken) {
        setLoading(false);
        setIsAuthenticated(false);
        return;
      }
      console.log('[VERIFY] accessToken:', accessToken);
      console.log('[VERIFY] refreshToken:', refreshToken);

      try {
        const userData = await apiFetch('/me/');
        setUser(userData);
        setIsAuthenticated(true);
      } catch (err) {
        logout();
      } finally {
        setLoading(false);
      }
    }

    verifyUser();
  }, [accessToken, refreshToken]);

  const login = async (accessToken, refreshToken) => {
    console.log('[APP] isAuthenticated:', isAuthenticated);

    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setAccessToken(accessToken);
    setRefreshToken(refreshToken);
    setLoading(true);

    // Fetch user info after login
    try {
      const userData = await apiFetch('/me/');
      console.log('AuthProv userData:', userData);
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (err) {
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    console.log('[LOGOUT] Clearing auth state');
    localStorage.clear();
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
