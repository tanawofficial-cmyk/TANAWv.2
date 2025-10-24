// Analytics API integration
import api from '../api';

const ANALYTICS_BASE_URL = process.env.REACT_APP_ANALYTICS_SERVICE_URL || 'http://localhost:5001';

export const analyticsApi = {
  // Get analytics results for a specific analysis
  getAnalyticsResults: async (analysisId) => {
    try {
      const response = await api.get(`${ANALYTICS_BASE_URL}/api/analytics/${analysisId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics results:', error);
      throw error;
    }
  },

  // Export analytics in various formats
  exportAnalytics: async (analysisId, format = 'json') => {
    try {
      const response = await api.get(`${ANALYTICS_BASE_URL}/api/analytics/${analysisId}/export`, {
        params: { format },
        responseType: format === 'json' ? 'json' : 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting analytics:', error);
      throw error;
    }
  },

  // Get available analytics types
  getAnalyticsTypes: async () => {
    try {
      const response = await api.get(`${ANALYTICS_BASE_URL}/api/analytics/types`);
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics types:', error);
      throw error;
    }
  },

  // Submit user feedback
  submitFeedback: async (feedbackData) => {
    try {
      const response = await api.post(`${ANALYTICS_BASE_URL}/api/feedback`, feedbackData);
      return response.data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  },

  // Get system statistics
  getSystemStatistics: async () => {
    try {
      const response = await api.get(`${ANALYTICS_BASE_URL}/api/statistics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system statistics:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get(`${ANALYTICS_BASE_URL}/api/health`);
      return response.data;
    } catch (error) {
      console.error('Error checking analytics service health:', error);
      throw error;
    }
  }
};

export default analyticsApi;
