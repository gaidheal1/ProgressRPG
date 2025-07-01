import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('refreshToken'));
  const [user, setUser] = useState(null); // Optional: store user info
  const [isAuthenticated, setIsAuthenticated] = useState(!!accessToken);

  const authFetch = async (url, options = {}) => {
    const headers = {
      ...(options.headers || {}),
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    };

    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) throw new Error('Not authenticated');
    return response.json();
  };

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const refresh = localStorage.getItem('refreshToken');

    if (token && refresh) {
      setAccessToken(token);
      setRefreshToken(refresh);
      setIsAuthenticated(true);
    }
  }, []);

  const login = (access, refresh) => {
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    setAccessToken(access);
    setRefreshToken(refresh);
    setIsAuthenticated(true);
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
    login,
    logout,
    user,
    setUser,
    authFetch,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
