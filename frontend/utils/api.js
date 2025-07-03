// src/utils/api.js
const API_URL = `${import.meta.env.VITE_API_BASE_URL}/api/v1`;

function clearAuthAndRedirect() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');

  // Redirect to login or show login modal
  window.location.href = '/#/login'; // ✅ Direct browser redirect
}


async function tryRefreshToken(refreshToken) {
  try {
    const res = await fetch(`${API_URL}/auth/jwt/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) return false;

    const data = await res.json();
    // Assuming the new access token is returned as data.access_token
    console.log("data:", data);
    localStorage.setItem('accessToken', data.access_token);
    // Optionally update refresh token if backend sends a new one
    if (data.refresh_token) {
      localStorage.setItem('refreshToken', data.refresh_token);
    }
    return true;
  } catch {
    return false;
  }
}


export async function apiFetch(path, options = {}) {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');

  const headers = {
    ...(options.headers || {}),
    Authorization: accessToken ? `Bearer ${accessToken}` : undefined,
    'Content-Type': 'application/json',
  };

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });


  if (response.status === 401 && refreshToken) {
    const refreshSuccess = await tryRefreshToken(refreshToken);

    if (refreshSuccess) {
      // Retry original request with new token
      const newAccessToken = localStorage.getItem('accessToken');
      const newHeaders = {
        ...headers,
        Authorization: `Bearer ${newAccessToken}`,
      };
      response = await fetch(url, { ...options, headers: newHeaders });
    } else {
      // Refresh failed, clear tokens and redirect to login
      clearAuthAndRedirect();
      throw new Error('Unauthorized');
    }
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `HTTP ${response.status}`);
  }

  return response.json();
}
