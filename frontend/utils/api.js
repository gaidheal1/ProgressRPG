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
    const response = await fetch(`${API_URL}/auth/jwt/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) return false;

    const data = await response.json();
    console.log("data:", data);

    localStorage.setItem('accessToken', data.access_token);
    // Optionally update refresh token if backend sends a new one
    if (data.access) {
      localStorage.setItem('accessToken', data.access);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}


export async function apiFetch(path, options = {}) {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  const fullPath = `${API_URL}${path}`;
  const headers = {
    ...(options.headers || {}),
    Authorization: accessToken ? `Bearer ${accessToken}` : undefined,
    'Content-Type': 'application/json',
  };

  const response = await fetch(fullPath, {
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

      response = await fetch(fullPath, { ...options, headers: newHeaders });
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
