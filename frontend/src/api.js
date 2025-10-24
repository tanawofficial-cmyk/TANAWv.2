import axios from "axios";

// Main backend API (authentication, user management, etc.)
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000/api",
});

// Analytics service API (file upload, analysis, etc.)
const analyticsApi = axios.create({
  baseURL: process.env.REACT_APP_ANALYTICS_API_URL || "http://localhost:5002/api",
});

// Session expiration callback
let sessionExpiredCallback = null;

// Register a callback to be called when session expires
export const setSessionExpiredCallback = (callback) => {
  sessionExpiredCallback = callback;
};

// Common interceptors
const normalizeResponse = (response) => {
  console.log("🔍 Axios interceptor - response.data type:", typeof response.data);
  console.log("🔍 Axios interceptor - response.headers:", response.headers);
  
  // If data is a string and looks like JSON, parse it
  if (typeof response.data === 'string' && (response.data.startsWith('{') || response.data.startsWith('['))) {
    console.log("⚠️ Response data is a string - parsing JSON in interceptor");
    try {
      return JSON.parse(response.data);
    } catch (e) {
      console.error("❌ Failed to parse JSON in interceptor:", e);
      return response.data;
    }
  }
  
  return response.data;
};
const normalizeError = (error) => {
  console.error("❌ API error:", error.response?.data || error.message);
  
  // Check for session expiration (401 Unauthorized)
  if (error.response?.status === 401) {
    console.warn("⚠️ Session expired or unauthorized");
    if (sessionExpiredCallback) {
      sessionExpiredCallback();
    }
  }
  
  if (error.response?.data) {
    return Promise.reject({
      success: false,
      message: error.response.data.message || "Server error",
      errors: error.response.data.errors || null,
      status: error.response.status,
    });
  }
  return Promise.reject({
    success: false,
    message: "Network error. Please try again.",
  });
};

// Main API interceptors
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(normalizeResponse, normalizeError);

// Analytics API interceptors
analyticsApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

analyticsApi.interceptors.response.use(normalizeResponse, normalizeError);

export default api;
export { analyticsApi };
