let API_BASE_URL;

if (window.location.hostname === 'staging.progressrpg.com') {
  API_BASE_URL = 'https://staging.progressrpg.com/';
} else if (window.location.hostname === 'app.progressrpg.com') {
  API_BASE_URL = 'https://app.progressrpg.com/';
} else {
  API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/';
}

export { API_BASE_URL };
