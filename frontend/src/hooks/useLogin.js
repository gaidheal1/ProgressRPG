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

      const message =
        typeof error === 'string'
          ? error.toLowerCase()
          : error?.message?.toLowerCase?.() || '';


      if (message.includes('no active account')) {
        return { success: false, error: 'Invalid email or password; please try again.' };
      } else {
        return {
          success: false,
          error: 'Login failed. Please try again.'
        };
      }
    }
  }, []);

  return login;
}
