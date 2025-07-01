// hooks/useLogin.js
import { useCallback } from 'react';
import { apiFetch } from '../../utils/api';

export default function useLogin() {
  const login = useCallback(async (email, password) => {
    try {

      const data = await apiFetch('/auth/jwt/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);

      return { success: true, tokens: data };
    } catch (error) {
      console.error('[useLogin] Error logging in:', error);
      return { success: false, error: 'Network error. Try again.' };
    }
  }, []);

  return login;
}
