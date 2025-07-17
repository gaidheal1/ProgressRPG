// hooks/useRegister.js
import { useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

const API_URL = `${import.meta.env.VITE_API_BASE_URL}/api/v1`;

export default function useRegister() {
  const { login } = useAuth();

  const register = useCallback(async (email, password1, password2, inviteCode, agreeToTerms) => {
    try {
      const response = await fetch(`${API_URL}/auth/registration/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password1,
          password2,
          invite_code: inviteCode,
          agree_to_terms: agreeToTerms
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          errors: data,
          errorMessage: data?.non_field_errors?.[0] || 'Registration failed.',
        }
      }

      const { accessToken, refreshToken } = data;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);

      // Await login to make sure state is set before continuing
      await login(accessToken, refreshToken);

      return { success: true };
    } catch (err) {
      console.error('[useRegister] Unexpected error:', err);
      return {
        success: false,
        errors: null,
        errorMessage: data?.non_field_errors?.[0] || 'Something went wrong, please try again.',
      };
    }
  }, [login]);

  return register;
}
