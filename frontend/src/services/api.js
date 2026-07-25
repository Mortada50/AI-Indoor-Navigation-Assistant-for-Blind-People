import axios from 'axios';

// Initialize the Axios client with centralized configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Accept': 'application/json',
  }
});

// Optionally, interceptors could be added here later if needed
// for logging, auth headers, or generic error handling

export default api;
