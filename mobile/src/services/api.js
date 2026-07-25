import axios from 'axios';

// Get base URL from Expo environment variables
// In development, this might be your local IP: http://192.168.1.100:5000
// In production, this would be your Render URL
const baseURL = process.env.EXPO_PUBLIC_API_BASE_URL || 'https://ai-indoor-navigation-assistant-for-blind.onrender.com';

const api = axios.create({
  baseURL,
  timeout: 15000, // YOLO inference can take a bit on CPU
  headers: {
    'Accept': 'application/json',
  }
});

export default api;
