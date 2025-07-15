// src/utils/api.js
import { jwtDecode } from "jwt-decode";

const API_URL = `${import.meta.env.VITE_API_BASE_URL}/api/v1`;


function isTokenExpiringSoon(token, bufferSeconds = 60) {
  try {
    const { exp } = jwtDecode(token);
    const now = Date.now() / 1000;
    return exp - now < bufferSeconds;
  } catch (err) {
    return true; // treat invalid token as expiring
  }
}

function clearAuthAndRedirect() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');

  // Redirect to login or show login modal
  window.location.href = '/#/login'; // ✅ Direct browser redirect
}


async function refreshAccessToken(refreshToken) {
  try {
    const response = await fetch(`${API_URL}/auth/jwt/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) throw new Error('Failed to refresh access token');

    const data = await response.json();

    if (data.access_token) {
      localStorage.setItem('accessToken', data.access_token);
      return data.access_token;
    }
    throw new Error('No access token returned from refresh');;
  } catch {
    return false;
  }
}


async function getValidAccessToken() {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  if (!accessToken || !refreshToken) throw new Error('Missing tokens');

  if (isTokenExpiringSoon(accessToken)) {
    const newAccess = await refreshAccessToken(refreshToken);
    if (!newAccess) throw new Error('Token refresh failed');
    return newAccess;
  }

  return accessToken;
}


export async function apiFetch(path, options = {}, explicitAccessToken=null) {
  try {
    const accessToken = explicitAccessToken || await getValidAccessToken();

    if (!accessToken) {
      throw new Error('No access token available for request');
    }

    const headers = {
      ...(options.headers || {}),
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    };

    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      clearAuthAndRedirect();
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'API error');
    }

    return response.json();
  } catch (err) {
    console.error('apiFetch error:', err);
    throw err;
  }
}
